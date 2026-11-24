! D-039 qualification commands. No full-interval trajectory continuation.
module assembly_qualification
  use native_adapter
  use diagnostic_native, only: export_maps,dump_matrix,diagnostic_directions,check_baseline_identity
  use reaction_data, only: csect1,csect2,csect3,csect4,b1,b2,b3,b4
  implicit none
contains
  subroutine check_assembly_identity(f,variant_reference,original_reference,quad_reference,workspace,branches)
    real(dp),intent(in) :: f(160),variant_reference(160),original_reference(160),workspace(:)
    integer(int8),intent(in) :: quad_reference(2560)
    integer,intent(in) :: branches(branch_size)
    call check_baseline_identity(f,variant_reference,workspace,branches)
    if (.not.unchanged_real_bits(last_original_rhs,original_reference)) call fail('assembly original F identity mismatch')
    if (any(transfer(aq_totals,quad_reference,2560)/=quad_reference)) call fail('assembly quad total identity mismatch')
  end subroutine check_assembly_identity

  subroutine run_assembly_qualification(command,base,time,temp,density,initial_variant,coordinate)
    character(*),intent(in) :: command
    real(dp),intent(in) :: base(160),time,temp,density,initial_variant(160)
    integer,intent(in) :: coordinate
    real(dp) :: original_reference(160),f(160),matrix(160,160),matrices(160,160,4)
    real(dp),allocatable :: reference_workspace(:)
    integer(int8) :: quad_reference(2560)
    integer :: branches(branch_size),i,unit,repeats
    integer(int64) :: before_count,after_count
    logical :: complete,completes(4),ok
    character(160) :: reason
    character(40) :: original_name,assembly_name
    call export_maps()
    original_reference=last_original_rhs
    quad_reference=transfer(aq_totals,quad_reference,2560)
    branches=branch_signature
    reference_workspace=[last_evaluated_eos,csect1(:,1),csect2(:,1),csect3(:,1),csect4(:,1), &
                         b1(:,1),b2(:,1),b3(:,1),b4(:,1)]
    call save_assembly_workspace('baseline-001.bin','assembly-baseline-001.bin')
    if (command=='assembly-repeat-3'.or.command=='assembly-repeat-1') then
      repeats=1
      if (command=='assembly-repeat-3') repeats=3
      do i=2,repeats
        assembly_role=2; assembly_context=i
        call fresh(base,time,temp,density,f,ok,reason)
        if (.not.ok) call fail('assembly repeat '//trim(reason))
        call check_assembly_identity(f,initial_variant,original_reference,quad_reference,reference_workspace,branches)
        write(original_name,'(a,i3.3,a)') 'baseline-',i,'.bin'
        write(assembly_name,'(a,i3.3,a)') 'assembly-baseline-',i,'.bin'
        call save_assembly_workspace(trim(original_name),trim(assembly_name))
      enddo
      return
    endif
    if (command/='assembly-diagnose') call fail('unsupported assembly qualification command')
    before_count=rhs_count
    call full_jacobian(base,time,temp,density,f,matrix,complete=complete)
    after_count=rhs_count
    call check_assembly_identity(f,initial_variant,original_reference,quad_reference,reference_workspace,branches)
    call dump_matrix('jacobian-factor-1.bin',matrix)
    open(newunit=unit,file='matrix-status.bin',status='new',access='stream',form='unformatted')
    write(unit) 1.0_dp,real(jacobian_count,dp),merge(1.0_dp,0.0_dp,complete),real(before_count,dp),real(after_count,dp)
    close(unit)
    matrices=ieee_value(0.0_dp,ieee_quiet_nan); completes=.false.
    matrices(:,:,2)=matrix; completes(2)=complete
    call diagnostic_directions(base,time,temp,density,initial_variant,coordinate,matrices,completes)
    call check_assembly_identity(ydot(:,1),initial_variant,original_reference,quad_reference,reference_workspace,branches)
  end subroutine run_assembly_qualification
end module assembly_qualification
