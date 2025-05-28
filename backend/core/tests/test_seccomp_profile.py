import pytest
import json
import os
from pathlib import Path

class SeccompProfileTest:
    @pytest.fixture
    def seccomp_path(self):
        """Get the path to the seccomp profile."""
        return Path(__file__).parent.parent.parent / 'sandbox' / 'seccomp.json'
        
    @pytest.fixture
    def seccomp_profile(self, seccomp_path):
        """Load the seccomp profile."""
        with open(seccomp_path) as f:
            return json.load(f)
            
    def test_profile_exists(self, seccomp_path):
        """Test that the seccomp profile exists."""
        assert seccomp_path.exists()
        
    def test_profile_structure(self, seccomp_profile):
        """Test that the seccomp profile has the correct structure."""
        assert 'defaultAction' in seccomp_profile
        assert 'archMap' in seccomp_profile
        assert 'syscalls' in seccomp_profile
        
    def test_default_action(self, seccomp_profile):
        """Test that the default action is set to SCMP_ACT_ERRNO."""
        assert seccomp_profile['defaultAction'] == 'SCMP_ACT_ERRNO'
        
    def test_arch_map(self, seccomp_profile):
        """Test that the architecture map is correctly configured."""
        arch_map = seccomp_profile['archMap']
        assert 'SCMP_ARCH_X86_64' in arch_map
        assert 'SCMP_ARCH_X86' in arch_map['SCMP_ARCH_X86_64']
        assert 'SCMP_ARCH_X32' in arch_map['SCMP_ARCH_X86_64']
        
    def test_syscalls(self, seccomp_profile):
        """Test that the syscalls list is properly configured."""
        syscalls = seccomp_profile['syscalls']
        assert isinstance(syscalls, list)
        assert len(syscalls) > 0
        
        # Test that each syscall has the required fields
        for syscall in syscalls:
            assert 'name' in syscall
            assert 'action' in syscall
            assert syscall['action'] == 'SCMP_ACT_ALLOW'
            
    def test_required_syscalls(self, seccomp_profile):
        """Test that all required syscalls are allowed."""
        required_syscalls = {
            'read', 'write', 'open', 'close', 'stat', 'fstat',
            'lstat', 'poll', 'lseek', 'mmap', 'mprotect', 'munmap',
            'brk', 'rt_sigaction', 'rt_sigprocmask', 'rt_sigreturn',
            'ioctl', 'pread64', 'pwrite64', 'readv', 'writev',
            'access', 'pipe', 'select', 'sched_yield', 'mremap',
            'msync', 'mincore', 'madvise', 'shmget', 'shmat',
            'shmctl', 'dup', 'dup2', 'pause', 'nanosleep',
            'getitimer', 'alarm', 'setitimer', 'getpid', 'sendfile',
            'socket', 'connect', 'accept', 'sendto', 'recvfrom',
            'sendmsg', 'recvmsg', 'shutdown', 'bind', 'listen',
            'getsockname', 'getpeername', 'socketpair', 'setsockopt',
            'getsockopt', 'clone', 'fork', 'vfork', 'execve',
            'wait4', 'kill', 'uname', 'fcntl', 'flock', 'fsync',
            'fdatasync', 'truncate', 'ftruncate', 'getdents',
            'getcwd', 'chdir', 'fchdir', 'rename', 'mkdir', 'rmdir',
            'creat', 'link', 'unlink', 'symlink', 'readlink',
            'chmod', 'fchmod', 'chown', 'fchown', 'lchown',
            'umask', 'gettimeofday', 'getrlimit', 'getrusage',
            'sysinfo', 'times', 'ptrace', 'getuid', 'syslog',
            'getgid', 'setuid', 'setgid', 'geteuid', 'getegid',
            'setpgid', 'getppid', 'getpgrp', 'setsid', 'setreuid',
            'setregid', 'getgroups', 'setgroups', 'setresuid',
            'getresuid', 'setresgid', 'getresgid', 'getpgid',
            'setfsuid', 'setfsgid', 'getsid', 'capget', 'capset',
            'rt_sigpending', 'rt_sigtimedwait', 'rt_sigqueueinfo',
            'rt_sigsuspend', 'sigaltstack', 'utime', 'mknod',
            'uselib', 'personality', 'ustat', 'statfs', 'fstatfs',
            'sysfs', 'getpriority', 'setpriority', 'sched_setparam',
            'sched_getparam', 'sched_setscheduler', 'sched_getscheduler',
            'sched_get_priority_max', 'sched_get_priority_min',
            'sched_rr_get_interval', 'mlock', 'munlock', 'mlockall',
            'munlockall', 'vhangup', 'modify_ldt', 'pivot_root',
            'prctl', 'arch_prctl', 'adjtimex', 'setrlimit',
            'chroot', 'sync', 'acct', 'settimeofday', 'mount',
            'umount2', 'swapon', 'swapoff', 'reboot', 'sethostname',
            'setdomainname', 'iopl', 'ioperm', 'create_module',
            'init_module', 'delete_module', 'get_kernel_syms',
            'query_module', 'quotactl', 'nfsservctl', 'getpmsg',
            'putpmsg', 'afs_syscall', 'tuxcall', 'security',
            'gettid', 'readahead', 'setxattr', 'lsetxattr',
            'fsetxattr', 'getxattr', 'lgetxattr', 'fgetxattr',
            'listxattr', 'llistxattr', 'flistxattr', 'removexattr',
            'lremovexattr', 'fremovexattr', 'tkill', 'time',
            'futex', 'sched_setaffinity', 'sched_getaffinity',
            'set_thread_area', 'io_setup', 'io_destroy', 'io_getevents',
            'io_submit', 'io_cancel', 'get_thread_area', 'lookup_dcookie',
            'epoll_create', 'epoll_ctl_old', 'epoll_wait_old', 'remap_file_pages',
            'getdents64', 'set_tid_address', 'restart_syscall', 'semtimedop',
            'fadvise64', 'timer_create', 'timer_settime', 'timer_gettime',
            'timer_getoverrun', 'timer_delete', 'clock_settime', 'clock_gettime',
            'clock_getres', 'clock_nanosleep', 'exit_group', 'epoll_wait',
            'epoll_ctl', 'tgkill', 'utimes', 'mbind', 'set_mempolicy',
            'get_mempolicy', 'mq_open', 'mq_unlink', 'mq_timedsend',
            'mq_timedreceive', 'mq_notify', 'mq_getsetattr', 'kexec_load',
            'waitid', 'add_key', 'request_key', 'keyctl', 'ioprio_set',
            'ioprio_get', 'inotify_init', 'inotify_add_watch', 'inotify_rm_watch',
            'migrate_pages', 'openat', 'mkdirat', 'mknodat', 'fchownat',
            'futimesat', 'newfstatat', 'unlinkat', 'renameat', 'linkat',
            'symlinkat', 'readlinkat', 'fchmodat', 'faccessat', 'pselect6',
            'ppoll', 'unshare', 'set_robust_list', 'get_robust_list',
            'splice', 'tee', 'sync_file_range', 'vmsplice', 'move_pages',
            'utimensat', 'epoll_pwait', 'signalfd', 'timerfd_create',
            'eventfd', 'fallocate', 'timerfd_settime', 'timerfd_gettime',
            'accept4', 'signalfd4', 'eventfd2', 'epoll_create1', 'dup3',
            'pipe2', 'inotify_init1', 'preadv', 'pwritev', 'rt_tgsigqueueinfo',
            'perf_event_open', 'recvmmsg', 'fanotify_init', 'fanotify_mark',
            'prlimit64', 'name_to_handle_at', 'open_by_handle_at', 'clock_adjtime',
            'syncfs', 'sendmmsg', 'setns', 'getcpu', 'process_vm_readv',
            'process_vm_writev', 'kcmp', 'finit_module', 'sched_setattr',
            'sched_getattr', 'renameat2', 'seccomp', 'getrandom', 'memfd_create',
            'kexec_file_load', 'bpf', 'execveat', 'userfaultfd', 'membarrier',
            'mlock2', 'copy_file_range', 'preadv2', 'pwritev2', 'pkey_mprotect',
            'pkey_alloc', 'pkey_free', 'statx', 'io_pgetevents', 'rseq'
        }
        
        allowed_syscalls = {syscall['name'] for syscall in seccomp_profile['syscalls']}
        missing_syscalls = required_syscalls - allowed_syscalls
        
        assert not missing_syscalls, f"Missing required syscalls: {missing_syscalls}"
        
    def test_dangerous_syscalls(self, seccomp_profile):
        """Test that dangerous syscalls are not allowed."""
        dangerous_syscalls = {
            'ptrace', 'reboot', 'mount', 'umount2', 'swapon', 'swapoff',
            'syslog', 'setuid', 'setgid', 'setreuid', 'setregid',
            'setresuid', 'setresgid', 'setfsuid', 'setfsgid',
            'capset', 'personality', 'acct', 'settimeofday',
            'adjtimex', 'clock_settime', 'settimeofday', 'stime',
            'vhangup', 'pivot_root', 'chroot', 'modify_ldt',
            'prctl', 'arch_prctl', 'setrlimit', 'mlock', 'mlock2',
            'mlockall', 'munlock', 'munlockall', 'mprotect',
            'brk', 'mmap', 'munmap', 'mremap', 'remap_file_pages',
            'msync', 'mincore', 'madvise', 'shmget', 'shmat',
            'shmctl', 'shmdt', 'msgget', 'msgsnd', 'msgrcv',
            'msgctl', 'semget', 'semop', 'semctl', 'semtimedop',
            'shutdown', 'socket', 'socketpair', 'bind', 'connect',
            'listen', 'accept', 'accept4', 'getsockname', 'getpeername',
            'sendto', 'recvfrom', 'sendmsg', 'recvmsg', 'getsockopt',
            'setsockopt', 'shutdown', 'sendfile', 'sendfile64',
            'sendmmsg', 'recvmmsg', 'accept4', 'epoll_create',
            'epoll_create1', 'epoll_ctl', 'epoll_wait', 'epoll_pwait',
            'eventfd', 'eventfd2', 'signalfd', 'signalfd4', 'timerfd_create',
            'timerfd_settime', 'timerfd_gettime', 'inotify_init',
            'inotify_init1', 'inotify_add_watch', 'inotify_rm_watch',
            'fanotify_init', 'fanotify_mark', 'name_to_handle_at',
            'open_by_handle_at', 'clock_adjtime', 'syncfs', 'setns',
            'sendmmsg', 'recvmmsg', 'accept4', 'fanotify_init',
            'fanotify_mark', 'prlimit64', 'sendmmsg', 'recvmmsg',
            'renameat2', 'seccomp', 'getrandom', 'memfd_create',
            'execveat', 'mlock2', 'copy_file_range', 'preadv2',
            'pwritev2', 'pkey_mprotect', 'pkey_alloc', 'pkey_free',
            'statx', 'io_pgetevents', 'rseq', 'pidfd_send_signal',
            'io_uring_setup', 'io_uring_enter', 'io_uring_register',
            'open_tree', 'move_mount', 'fsopen', 'fsconfig', 'fsmount',
            'fspick', 'pidfd_open', 'clone3', 'close_range', 'openat2',
            'pidfd_getfd', 'faccessat2', 'process_madvise', 'epoll_pwait2',
            'mount_setattr', 'quotactl_fd', 'landlock_create_ruleset',
            'landlock_add_rule', 'landlock_restrict_self', 'memfd_secret',
            'process_mrelease', 'futex_waitv', 'set_mempolicy_home_node'
        }
        
        allowed_syscalls = {syscall['name'] for syscall in seccomp_profile['syscalls']}
        dangerous_allowed = dangerous_syscalls & allowed_syscalls
        
        assert not dangerous_allowed, f"Dangerous syscalls allowed: {dangerous_allowed}"
        
    def test_profile_format(self, seccomp_profile):
        """Test that the seccomp profile has the correct format."""
        # Test that the profile is a valid JSON object
        assert isinstance(seccomp_profile, dict)
        
        # Test that all required fields are present
        assert 'defaultAction' in seccomp_profile
        assert 'archMap' in seccomp_profile
        assert 'syscalls' in seccomp_profile
        
        # Test that syscalls is a list
        assert isinstance(seccomp_profile['syscalls'], list)
        
        # Test that each syscall has the required fields
        for syscall in seccomp_profile['syscalls']:
            assert isinstance(syscall, dict)
            assert 'name' in syscall
            assert 'action' in syscall
            assert isinstance(syscall['name'], str)
            assert isinstance(syscall['action'], str)
            
    def test_profile_values(self, seccomp_profile):
        """Test that the seccomp profile values are correct."""
        # Test default action
        assert seccomp_profile['defaultAction'] == 'SCMP_ACT_ERRNO'
        
        # Test architecture map
        arch_map = seccomp_profile['archMap']
        assert isinstance(arch_map, dict)
        assert 'SCMP_ARCH_X86_64' in arch_map
        assert isinstance(arch_map['SCMP_ARCH_X86_64'], list)
        
        # Test syscalls
        syscalls = seccomp_profile['syscalls']
        assert isinstance(syscalls, list)
        assert len(syscalls) > 0
        
        for syscall in syscalls:
            assert syscall['action'] == 'SCMP_ACT_ALLOW' 