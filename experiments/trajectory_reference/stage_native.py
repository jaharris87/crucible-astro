#!/usr/bin/env python3
"""Hash-check and copy the fixed native closure; never compile or evaluate it.

prepare SOURCE_CONFIG NEW_DEST stages every original, exact adapted diff, public
source and manifest. SOURCE_CONFIG supplies ``files`` with the rhs_reference bindings. The two
protocol numerical files are hash-bound and resolved beside xnet_integrate
unless --native-source-dir is supplied (same relative refs/producer paths).
verify DEST rechecks all source/input bytes before a fresh build.
"""

import argparse
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRA = {
    "refs/producer/xnet_integrate_be.f90": "4fddd97ecb1e08bfdf29dec948517cb90e2b0353ddcc765a6858dd0cd5818852",
    "refs/producer/xnet_jacobian_dense.f90": "5de0d789e2a055fe6a409287cd64124832a1645a5b1edd9ad05f0ba806417d38",
}
PUBLIC = (
    "stage_native.py",
    "native_adapter.f90",
    "trajectory_driver.f90",
    "phase2d_branch_state.f90",
    "synthetic_modules.f90",
    "synthetic_native.f90",
    "forcing_stub.f90",
    "forcing_synthetic.f90",
    "build.sh",
    "PROTOCOL.md",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Source transform expected one occurrence: {old[:90]!r}")
    return text.replace(old, new)


def adapt(name, text):
    if name.endswith("xnet_conditions.f90"):
        start = text.index("  Subroutine t9rhofind(")
        end = text.index("  End Subroutine t9rhofind", start) + len(
            "  End Subroutine t9rhofind"
        )
        text = (
            text[:start]
            + """  Subroutine t9rhofind(kstep,tf,nf,t9f,rhof,mask_in)
    Use, intrinsic :: ieee_arithmetic
    Use xnet_controls, Only: nzevolve, zb_lo, zb_hi, lzactive
    Implicit None
    Integer, Intent(in) :: kstep
    Real(dp), Intent(in) :: tf(nzevolve)
    Integer, Intent(inout) :: nf(nzevolve)
    Real(dp), Intent(inout) :: t9f(nzevolve), rhof(nzevolve)
    Logical, Optional, Target, Intent(in) :: mask_in(zb_lo:zb_hi)
    Logical, Pointer :: mask(:)
    Integer :: i, n
    Real(dp) :: fraction
    If (present(mask_in)) Then
      mask(zb_lo:) => mask_in
    Else
      mask(zb_lo:) => lzactive(zb_lo:zb_hi)
    EndIf
    Do i=zb_lo,zb_hi
      If (.not.mask(i)) Cycle
      If (nh(i)<2) Error Stop 'Forcing needs two knots'
      If (.not.all(ieee_is_finite(th(1:nh(i),i)))) Error Stop 'Nonfinite forcing time'
      If (.not.all(ieee_is_finite(t9h(1:nh(i),i)))) Error Stop 'Nonfinite forcing T9'
      If (.not.all(ieee_is_finite(rhoh(1:nh(i),i)))) Error Stop 'Nonfinite forcing rho'
      If (any(th(2:nh(i),i)<=th(1:nh(i)-1,i))) Error Stop 'Nonincreasing forcing'
      If (any(t9h(1:nh(i),i)<=0).or.any(rhoh(1:nh(i),i)<=0)) Error Stop 'Nonpositive forcing'
      If (.not.ieee_is_finite(tf(i))) Error Stop 'Nonfinite forcing query'
      If (tf(i)<th(1,i).or.tf(i)>th(nh(i),i)) Error Stop 'Forcing outside closed coverage'
      Do n=1,nh(i)
        If (tf(i)<=th(n,i)) Exit
      EndDo
      nf(i)=n
      If (tf(i)==th(n,i)) Then
        t9f(i)=t9h(n,i)
        rhof(i)=rhoh(n,i)
      Else
        fraction=(tf(i)-th(n-1,i))/(th(n,i)-th(n-1,i))
        t9f(i)=t9h(n-1,i)+fraction*(t9h(n,i)-t9h(n-1,i))
        rhof(i)=rhoh(n-1,i)+fraction*(rhoh(n,i)-rhoh(n-1,i))
      EndIf
    EndDo
  End Subroutine t9rhofind"""
            + text[end:]
        )
    elif name.endswith("xnet_integrate_be.f90"):
        start = text.index("  Subroutine step_be(")
        end = text.index("  End Subroutine step_be", start) + len(
            "  End Subroutine step_be"
        )
        text = (
            text[:start]
            + """  Subroutine step_be(kstep,inr)
    Use xnet_controls, Only: zb_lo,zb_hi
    Use native_adapter, Only: adapted_step
    Implicit None
    Integer, Intent(in) :: kstep
    Integer, Intent(inout) :: inr(zb_lo:zb_hi)
    Call adapted_step(kstep,inr)
  End Subroutine step_be"""
            + text[end:]
        )
        text = replace_once(
            text,
            "      Call step_be(kstep,inr)",
            """      If (any(tdel <= 0.0).or.any(t+tdel <= t)) Error Stop 'Nonprogress retry'
      Write(lun_diag,*) 'BE_ATTEMPT',kstep,kts,tt,tdel
      Flush(lun_diag)
      Call step_be(kstep,inr)""",
        )
    elif name.endswith("xnet_jacobian_dense.f90"):
        text = replace_once(
            text,
            "\nModule xnet_jacobian\n",
            "\nModule xnet_jacobian\n  Use phase2d_branch_state, Only: abort_linear\n",
        )
        for call in ("dgesv", "dgetrf", "dgetrs"):
            lines = text.splitlines(keepends=True)
            hits = [i for i, line in enumerate(lines) if f"Call {call}(" in line]
            if len(hits) != 1:
                raise ValueError(f"Expected one {call}")
            i = hits[0]
            lines.insert(
                i + 1,
                f"        If (info(izb)/=0) Call abort_linear(info(izb),'{call}')\n",
            )
            text = "".join(lines)
    elif name.endswith("xnet_ffn.f90"):
        text = replace_once(
            text,
            "\nModule xnet_ffn\n",
            "\nModule xnet_ffn\n  Use phase2d_branch_state, Only: branch_signature,side\n",
        )
        text = replace_once(
            text,
            "        ! Bi-linear interpolation",
            "        branch_signature(1:2)=[lt1,le1]\n        ! Bi-linear interpolation",
        )
        text = replace_once(
            text,
            "          If ( rf(k,izb) < lrfmin ) Then",
            "          branch_signature(2+k)=side(rf(k,izb),lrfmin)\n          If ( rf(k,izb) < lrfmin ) Then",
        )
    elif name.endswith("xnet_screening.f90"):
        text = replace_once(
            text,
            "\nModule xnet_screening\n",
            "\nModule xnet_screening\n  Use phase2d_branch_state, Only: branch_signature,side\n",
        )
        for number, variable, offset in (
            (2, "lambda12", 200),
            (3, "lambda123", 9615),
            (4, "lambda1234", 9727),
        ):
            marker = f"        ! Select {'Screening' if number == 2 else 'screening'} factor for {number} reactant reactions"
            lines = [f"        Do j=1,nreac({number})"]
            for k, threshold in enumerate(
                ("lam_1", "lam_2", "lam_3", "lam_4", "lam_5", "lam_6")
            ):
                lines.append(
                    f"          branch_signature({offset}+7*(j-1)+{k})=side({variable}(j),{threshold})"
                )
            lines.extend(
                [
                    f"          branch_signature({offset}+7*(j-1)+6)=side(h{number}i(j),h{number}s(j))",
                    "        EndDo",
                ]
            )
            text = replace_once(text, marker, "\n".join(lines) + "\n" + marker)
    elif name.endswith("actual_eos.F90"):
        text = replace_once(
            text,
            "\nmodule actual_eos_module\n",
            "\nmodule actual_eos_module\n    use phase2d_branch_state, only: branch_signature,side\n",
        )
        text = replace_once(text, "    private\n", "    private\n    public :: d,t\n")
        text = replace_once(
            text,
            "           jat = max(1,min(jat,jtmax-1))",
            "           branch_signature(10021)=jat\n           jat = max(1,min(jat,jtmax-1))\n           branch_signature(10022)=jat",
        )
        text = replace_once(
            text,
            "           iat = max(1,min(iat,itmax-1))",
            "           branch_signature(10023)=iat\n           iat = max(1,min(iat,itmax-1))\n           branch_signature(10024)=iat",
        )
        text = replace_once(
            text,
            "           mxt = 1.0_dp - xt",
            "           branch_signature(10025)=side(temp,t(jat))\n           branch_signature(10026)=side(din,d(iat))\n           mxt = 1.0_dp - xt",
        )
    elif name.endswith("xnet_integrate.f90"):
        text = replace_once(
            text,
            "\nModule xnet_integrate\n",
            "\nModule xnet_integrate\n  Use phase2d_branch_state, Only: branch_signature,side\n",
        )
        text = replace_once(
            text,
            "          If ( csect3(k,izb) < 1.0e-20 ) csect3(k,izb) = 0.0",
            "          branch_signature(10000+k)=side(csect3(k,izb),1.0e-20_dp)\n          If ( csect3(k,izb) < 1.0e-20 ) csect3(k,izb) = 0.0",
        )
    return text


def stage(config_path, destination, native_source_dir=None):
    config = json.loads(Path(config_path).read_text())
    expected = (
        json.loads((HERE.parent / "rhs_reference/bindings.json").read_text())["files"]
        | EXTRA
    )
    files = dict(config["files"])
    native_dir = (
        Path(native_source_dir)
        if native_source_dir
        else Path(files["refs/producer/xnet_integrate.f90"]["path"]).parent
    )
    for name, digest in EXTRA.items():
        files.setdefault(
            name, {"path": str(native_dir / Path(name).name), "sha256": digest}
        )
    if set(files) != set(expected):
        raise ValueError("Exact pinned closure required")
    originals = {}
    for name, digest in expected.items():
        entry = files[name]
        path = Path(entry["path"])
        if (
            set(entry) != {"path", "sha256"}
            or not path.is_absolute()
            or entry["sha256"] != digest
        ):
            raise ValueError(f"Wrong source binding: {name}")
        before = path.stat()
        data = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ValueError(f"Source changed during copy: {name}")
        if sha(data) != digest:
            raise ValueError(f"Original hash mismatch: {name}")
        originals[name] = data
    dest = Path(destination).resolve()
    if dest.exists():
        raise ValueError("New immutable staging destination required")
    dest.mkdir(parents=True)
    transforms = {}
    for name, data in originals.items():
        new = (
            adapt(name, data.decode()).encode()
            if name.endswith((".f90", ".F90"))
            else data
        )
        for relative, payload in (("original/" + name, data), (name, new)):
            path = dest / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
            path.chmod(0o444)
        if new != data:
            delta = "".join(
                difflib.unified_diff(
                    data.decode().splitlines(True),
                    new.decode().splitlines(True),
                    fromfile="original/" + name,
                    tofile=name,
                )
            )
            path = dest / ("diffs/" + name + ".patch")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(delta)
            transforms[name] = {
                "original": sha(data),
                "adapted": sha(new),
                "diff": sha(delta.encode()),
            }
    for name in PUBLIC:
        (dest / name).write_bytes((HERE / name).read_bytes())
    (dest / "bindings.json").write_bytes(
        (HERE.parent / "rhs_reference/bindings.json").read_bytes()
    )
    manifest = {
        "schema": "crucible.trajectory-native-stage.v1",
        "configuration": config,
        "transforms": transforms,
        "files": {
            str(p.relative_to(dest)): {
                "bytes": p.stat().st_size,
                "sha256": sha(p.read_bytes()),
            }
            for p in sorted(dest.rglob("*"))
            if p.is_file()
        },
    }
    (dest / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n"
    )
    verify(dest)
    return manifest


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / "source-manifest.json").read_text())
    if manifest["schema"] != "crucible.trajectory-native-stage.v1":
        raise ValueError("Wrong stage manifest")
    for name, entry in manifest["files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe staged path")
        data = (root / path).read_bytes()
        if len(data) != entry["bytes"] or sha(data) != entry["sha256"]:
            raise ValueError(f"Staged bytes changed: {name}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("config")
    prep.add_argument("destination")
    prep.add_argument("--native-source-dir")
    ver = sub.add_parser("verify")
    ver.add_argument("root")
    args = parser.parse_args()
    result = (
        stage(args.config, args.destination, args.native_source_dir)
        if args.command == "prepare"
        else verify(args.root)
    )
    print(json.dumps({"schema": result["schema"], "files": len(result["files"])}))
