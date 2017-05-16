Github integration for clang-format using a heroku webapp
---------------------------------------------------------

This webapp creates a commit formatting a github repository using clang-format and creates a comment in the PR with the link to the commit.

To configure a repo to use this webapp, use comments in the `.clang-format` file in the repo root

    # version: 3.7
    # include: *.h
    # include: *.hpp
    # include: *.cpp
    # exclude: tpl/*
    # exlcude: contrib/*

Version can be from 3.3 - 3.9

Include directives give the files matching the pattern to be run through clang-format. Unix style globs are recognized

Exclude directives removes files matching the pattern



To set this up for your repository create a heroku app and install heroku cli locally. Run the steps below

- Add github oauth token to a github user whose account will be as the author of the commits and also as the commenter in the PR

    heroku config:set GH_TOKEN=""

- Add the following buildpacks

    heroku buildpacks:add https://github.com/ivandeex/heroku-buildpack-apt
    heroku buildpacks:add https://github.com/heroku/heroku-buildpack-python

- Configure `ivandeex/heroku-buildpack-apt` with apt sources

    heroku config:set APT_SOURCES="deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.6 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.6 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.7 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.7 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.8 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.8 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.9 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.9 main"
