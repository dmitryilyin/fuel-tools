#!/usr/bin/env python

import sys
import psutil


class KillProc:
    @classmethod
    def kill_pid(cls, pid):
        pid = int(pid)
        if not psutil.pid_exists(pid):
            return False
        process = psutil.Process(pid)
        process.terminate()
        try:
            process.wait(timeout=5)
        except psutil.TimeoutExpired:
            process.kill()
        if psutil.pid_exists(pid):
            return False
        else:
            return True

    @classmethod
    def kill_pid_and_children(cls, pid):
        pid = int(pid)
        if not psutil.pid_exists(pid):
            return []
        process = psutil.Process(pid)
        children = process.get_children(recursive=True)
        cls.kill_pid(pid)
        for child in children:
            cls.kill_pid(child.pid)

    @classmethod
    def get_children(cls, pid):
        pid = int(pid)
        if not psutil.pid_exists(pid):
            return []
        process = psutil.Process(pid)
        children = process.get_children(recursive=True)
        children_pids = [child.pid for child in children]
        children_pids.append(pid)
        return children_pids

    @classmethod
    def find_pids_of_python_processes(cls):
        for pid in psutil.process_iter():
            if len(pid.cmdline) > 1 and 'python' in pid.cmdline[0]:
                print pid.pid, pid.exe, pid.cmdline


if __name__ == "__main__":
    if len(sys.argv) == 3:
        action = sys.argv[1]
        pid = sys.argv[2]
        if action == 'kill':
            KillProc.kill_pid_and_children(pid)
        elif action == 'get':
            pids = KillProc.get_children(pid)
            print pids
        elif action == 'find':
            KillProc.find_pids_of_python_processes()