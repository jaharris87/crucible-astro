! Distinct numerical assembly only. This file alone adds -fp-model strict.
module assembly113_math
  use, intrinsic :: iso_fortran_env, only: real64,int8,int32,int64
  use, intrinsic :: ieee_arithmetic
  implicit none
  integer,parameter :: qp=selected_real_kind(33,4931)
contains
  subroutine precision_contract(ok,reason)
    logical,intent(out) :: ok
    character(*),intent(out) :: reason
    real(qp) :: zero,one
    integer(int64) :: words(2)
    type(ieee_round_type) :: rounding
    logical :: gradual
    ok=.false.; reason='unsupported binary128 kind/model'
    zero=0.0_qp; one=1.0_qp
    if (radix(zero)/=2.or.digits(zero)/=113.or.storage_size(zero)/=128) return
    if (minexponent(zero)/=-16381.or.maxexponent(zero)/=16384) return
    words=transfer(one,words)
    reason='unsupported binary128 little-endian representation'
    if (any(words/=[0_int64,int(z'3fff000000000000',int64)])) return
    words=transfer(-zero,words)
    if (any(words/=[0_int64,int(z'8000000000000000',int64)])) return
    reason='assembly requires unchanged gradual nearest arithmetic'
    call ieee_get_rounding_mode(rounding)
    if (rounding/=ieee_nearest) return
    if (.not.ieee_support_underflow_control()) return
    call ieee_get_underflow_mode(gradual)
    if (.not.gradual) return
    ok=.true.; reason='supported'
  end subroutine precision_contract

  subroutine write_kind_record()
    integer :: unit
    open(newunit=unit,file='assembly-kind.bin',status='new',access='stream',form='unformatted')
    write(unit) int(z'4352514b',int32),1_int32,2_int32,113_int32,128_int32,-16381_int32,16384_int32,1_int32
    close(unit)
  end subroutine write_kind_record

  subroutine assembly_modes(nearest,gradual)
    integer,intent(out) :: nearest,gradual
    type(ieee_round_type) :: rounding
    logical :: gradual_mode
    call ieee_get_rounding_mode(rounding)
    nearest=merge(1,0,rounding==ieee_nearest); gradual=-1
    if (ieee_support_underflow_control()) then
      call ieee_get_underflow_mode(gradual_mode)
      gradual=merge(1,0,gradual_mode)
    endif
  end subroutine assembly_modes

  logical function supported_quad(value)
    real(qp),intent(in) :: value
    supported_quad=ieee_is_finite(value)
    if (.not.supported_quad) return
    if (value/=0.0_qp) supported_quad=ieee_is_normal(value)
  end function supported_quad

  logical function exact_small_promotion(value,promoted)
    real(real64),intent(in) :: value
    real(qp),intent(in) :: promoted
    integer(int64) :: bits,fraction_bits
    real(qp) :: expected
    bits=transfer(value,bits)
    exact_small_promotion=.true.
    ! DAZ is not identified by the global underflow-mode query. Decode every
    ! actual zero/subnormal operand from integer bits, without binary64 math.
    if (ibits(bits,52,11)/=0) return
    fraction_bits=iand(bits,int(z'000fffffffffffff',int64))
    expected=scale(real(fraction_bits,qp),-1074)
    if (btest(bits,63)) expected=-expected
    exact_small_promotion=promoted==expected
    if (fraction_bits==0) exact_small_promotion=exact_small_promotion.and. &
      (ieee_is_negative(promoted).eqv.btest(bits,63))
  end function exact_small_promotion

  subroutine narrow113(value,out,ok,reason)
    real(qp),intent(in) :: value
    real(real64),intent(out) :: out
    logical,intent(out) :: ok
    character(*),intent(out) :: reason
    out=ieee_value(0.0_real64,ieee_quiet_nan)
    ok=.false.; reason='nonfinite binary128 total'
    if (.not.ieee_is_finite(value)) return
    out=real(value,real64)
    reason='binary64 return overflow'
    if (.not.ieee_is_finite(out)) return
    if (out==0.0_real64) then
      reason='binary64 return lost signed zero'
      if (ieee_is_negative(out).neqv.ieee_is_negative(value)) return
    endif
    ok=.true.; reason='supported'
  end subroutine narrow113

  subroutine assemble113(y,b,lo,hi,participants,f,totals,classes,products,running,absolute,ok,reason)
    real(real64),intent(in) :: y(:),b(:)
    integer,intent(in) :: lo(:,:),hi(:,:),participants(:,:)
    real(real64),intent(out) :: f(:)
    real(qp),intent(out) :: totals(:),classes(:,:),products(:),running(:),absolute(:)
    logical,intent(out) :: ok
    character(*),intent(out) :: reason
    real(qp),volatile :: term,operand,class_sum,total,abs_total
    integer :: i,o,e,r,m,seen(size(b))
    logical :: narrow_ok
    ok=.false.; reason='malformed assembly dimensions'
    if (size(y)<1) return
    if (size(lo,1)/=4.or.size(hi,1)/=4.or.size(lo,2)/=size(y).or.size(hi,2)/=size(y)) return
    if (size(participants,1)/=4.or.size(participants,2)/=size(b)) return
    if (size(f)/=size(y).or.size(totals)/=size(y).or.size(absolute)/=size(y)) return
    if (size(classes,1)/=4.or.size(classes,2)/=size(y)) return
    if (size(products)/=size(b).or.size(running)/=size(b).or.size(b)>6794) return
    f=ieee_value(0.0_real64,ieee_quiet_nan)
    totals=ieee_value(0.0_qp,ieee_quiet_nan); classes=totals(1)
    products=totals(1); running=totals(1); absolute=totals(1)
    reason='nonfinite assembly operand'
    if (.not.all(ieee_is_finite(y)).or..not.all(ieee_is_finite(b))) return
    reason='assembly abundance outside [0,1]'
    if (any(y<0.0_real64).or.any(y>1.0_real64)) return
    seen=0
    do i=1,size(y)
      abs_total=0.0_qp; m=3
      do o=1,4
        reason='malformed assembly range'
        if (lo(o,i)<1.or.lo(o,i)>size(b)+1.or.hi(o,i)<0.or.hi(o,i)>size(b)) return
        if (hi(o,i)<lo(o,i)-1) return
        class_sum=0.0_qp
        do e=lo(o,i),hi(o,i)
          seen(e)=seen(e)+1
          reason='malformed duplicate assembly entry'
          if (seen(e)/=1) return
          reason='malformed participant index'
          if (any(participants(1:o,e)<1).or.any(participants(1:o,e)>size(y))) return
          ! Promotion occurs before every multiplication, including b itself.
          term=real(b(e),qp)
          reason='inexact binary64 b promotion'
          if (.not.exact_small_promotion(b(e),term)) return
          do r=1,o
            operand=real(y(participants(r,e)),qp)
            reason='inexact binary64 abundance promotion'
            if (.not.exact_small_promotion(y(participants(r,e)),operand)) return
            term=term*operand
          enddo
          reason='unsupported binary128 product range'
          if (.not.supported_quad(term)) return
          products(e)=term
          class_sum=class_sum+term
          reason='unsupported binary128 class range'
          if (.not.supported_quad(class_sum)) return
          running(e)=class_sum
          abs_total=abs_total+abs(term)
          if (.not.supported_quad(abs_total)) return
          m=m+o+1
        enddo
        classes(o,i)=class_sum
      enddo
      reason='unsupported assembly operation count'
      if (m>33973) return
      ! Three explicit joins preserve native class order without contraction.
      total=classes(1,i)+classes(2,i)
      reason='unsupported binary128 joined range'
      if (.not.supported_quad(total)) return
      total=total+classes(3,i)
      if (.not.supported_quad(total)) return
      total=total+classes(4,i)
      if (.not.supported_quad(total)) return
      totals(i)=total; absolute(i)=abs_total
      call narrow113(total,f(i),narrow_ok,reason)
      if (.not.narrow_ok) return
    enddo
    reason='malformed unassigned assembly entry'
    ok=all(seen==1)
    if (ok) reason='supported'
  end subroutine assemble113

  subroutine precision_fixture(scenario,ok,reason)
    character(*),intent(in) :: scenario
    logical,intent(out) :: ok
    character(*),intent(out) :: reason
    real(real64),volatile :: operand,one,small,output
    real(qp),volatile :: promoted,qone,qsmall,tie
    real(real64) :: yy(2),bb(5),ff(2)
    real(qp) :: tt(2),cc(4,2),pp(5),rr(5),ww(2)
    integer :: lo(4,2),hi(4,2),parts(4,5),unit,k
    integer(int64) :: input_bits(10),expected(8),returned,expected_totals(4),observed_totals(4)
    logical :: accepted
    call precision_contract(ok,reason)
    if (.not.ok) return
    call write_kind_record()
    one=1.0_real64
    if (scenario=='precision') then
      input_bits=[0_int64,int(z'8000000000000000',int64),1_int64,int(z'8000000000000001',int64), &
        int(z'000fffffffffffff',int64),int(z'800fffffffffffff',int64),int(z'0010000000000000',int64), &
        int(z'8010000000000000',int64),int(z'3ff0000000000000',int64),int(z'bff0000000000000',int64)]
      open(newunit=unit,file='precision-values.bin',status='new',access='stream',form='unformatted')
      write(unit) int(z'43525150',int32),1_int32,10_int32,0_int32
      do k=1,10
        operand=transfer(input_bits(k),operand)
        promoted=real(operand,qp)
        call narrow113(promoted,output,accepted,reason)
        if (.not.accepted) then
          ok=.false.; close(unit); return
        endif
        returned=transfer(output,returned)
        write(unit) input_bits(k),promoted,returned
        if (returned/=input_bits(k)) then
          ok=.false.; reason='subnormal/signed exact promotion or return failed'; close(unit); return
        endif
        ! Verify promotion itself, not merely a possibly lossy round-trip pair.
        if (operand/=0.0_real64) then
          if (promoted/=scale(real(fraction(operand),qp),exponent(operand))) then
            ok=.false.; reason='binary64 operand promotion is not exact'; close(unit); return
          endif
        else if (ieee_is_negative(promoted).neqv.ieee_is_negative(operand)) then
          ok=.false.; reason='promotion lost signed zero'; close(unit); return
        endif
      enddo
      close(unit)
      small=transfer(1_int64,small); qsmall=real(small,qp); qone=real(one,qp)
      expected=[0_int64,int(z'8000000000000000',int64),2_int64,int(z'8000000000000002',int64), &
        int(z'0010000000000000',int64),int(z'8010000000000000',int64), &
        int(z'3ff0000000000000',int64),int(z'3ff0000000000002',int64)]
      open(newunit=unit,file='rounding-values.bin',status='new',access='stream',form='unformatted')
      write(unit) int(z'43525154',int32),1_int32,8_int32,0_int32
      do k=1,8
        select case(k)
        case(1)
          tie=qsmall/2.0_qp
        case(2)
          tie=-qsmall/2.0_qp
        case(3)
          tie=3.0_qp*qsmall/2.0_qp
        case(4)
          tie=-3.0_qp*qsmall/2.0_qp
        case(5)
          operand=transfer(int(z'000fffffffffffff',int64),operand)
          tie=real(operand,qp)+qsmall/2.0_qp
        case(6)
          tie=-(real(operand,qp)+qsmall/2.0_qp)
        case(7)
          tie=qone+scale(qone,-53)
        case(8)
          tie=qone+3.0_qp*scale(qone,-53)
        end select
        call narrow113(tie,output,accepted,reason)
        if (.not.accepted) then
          ok=.false.; close(unit); return
        endif
        returned=transfer(output,returned)
        write(unit) tie,returned,expected(k)
        if (returned/=expected(k)) then
          ok=.false.; reason='gradual nearest-even tie conversion failed'; close(unit); return
        endif
      enddo
      close(unit)
      ok=.true.; reason='precision and conversion fixtures passed'
      return
    endif
    yy=[real(one,real64),nearest(real(one,real64),-1.0_real64)]
    bb=[scale(real(one,real64),113),-scale(real(one,real64),113),1.0_real64,1.0_real64,scale(real(one,real64),-112)]
    lo(:,1)=[1,2,4,5]; hi(:,1)=lo(:,1)
    lo(:,2)=[2,3,5,6]; hi(:,2)=[1,3,4,5]
    parts=1; parts(1:2,3)=2
    if (scenario=='malformed') parts(1,3)=0
    if (scenario=='nonfinite') bb(1)=ieee_value(0.0_real64,ieee_quiet_nan)
    call assemble113(yy,bb,lo,hi,parts,ff,tt,cc,pp,rr,ww,accepted,reason)
    if (scenario=='malformed'.or.scenario=='nonfinite') then
      ok=.not.accepted
      if (.not.ok) reason='invalid assembly was incorrectly accepted'
      return
    endif
    if (.not.accepted) then
      ok=.false.; return
    endif
    if (scenario=='overflow') then
      promoted=real(huge(real(one,real64)),qp)*2.0_qp
      call narrow113(promoted,output,accepted,reason)
      ok=.not.accepted
      if (.not.ok) reason='overflow was incorrectly accepted'
      return
    endif
    if (scenario/='arithmetic') then
      ok=.false.; reason='unknown assembly fixture'; return
    endif
    ! Independent IEEE encodings of 1+2^-112 and (1-2^-53)^2.
    ! Public Fraction oracles verify these constants without native arithmetic.
    expected_totals=[int(z'0000000000000001',int64),int(z'3fff000000000000',int64), &
                     int(z'e000000000000080',int64),int(z'3ffeffffffffffff',int64)]
    observed_totals=transfer(tt,observed_totals)
    if (any(observed_totals/=expected_totals)) then
      ok=.false.; reason='ordered product/class exact-rational oracle failed'; return
    endif
    open(newunit=unit,file='arithmetic-proof.bin',status='new',access='stream',form='unformatted')
    write(unit) int(z'43525141',int32),1_int32,2_int32,5_int32
    write(unit) yy,bb,int(lo,int32),int(hi,int32),int(parts,int32),ff,tt,cc,pp,rr,ww
    close(unit)
    ok=.true.; reason='ordered product/class arithmetic passed'
  end subroutine precision_fixture
end module assembly113_math
