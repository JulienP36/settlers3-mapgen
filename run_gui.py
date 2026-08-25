import sys


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        from s3mapgen.package_runtime import main
    else:
        from s3mapgen.gui_v16_runtime import main
    main()
