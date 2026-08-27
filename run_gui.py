import sys


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        from s3mapgen.application.diagnostics.package_runtime import main
    else:
        from s3mapgen.application.runtime import main
    main()
