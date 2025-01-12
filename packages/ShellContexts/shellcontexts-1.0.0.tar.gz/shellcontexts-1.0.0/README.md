# ShellContexts

A few useful context managers for temporarily changing the environment.

```
ModificationContext
`- chdir
`- set_umask
`- increase_umask
`- decrease_umask
`- seteuid
`- setegid
```

They are simple wrappers around the syscalls in their names. Therefore they are not thread-safe, so use them sanely. They are however reentry safe :)

`chdir` serves the same purpose as `contextlib.chdir`. It is here for completion-ist sake, and to demonstrate the abstraction provided by `ModificationContext`.

[We decided](https://discuss.python.org/t/add-umask-to-contextlib/75809) to not add the rest to the standard library, in `shutil` or `contextlib`, whence I decided to make this package.

## Installing

Available on PyPI as [ShellContexts](https://pypi.org/project/ShellContexts/)

```
$ pip install ShellContexts
```
