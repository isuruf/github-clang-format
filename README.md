- heroku config:set APT_SOURCES="deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.6 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.6 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.7 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.7 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.8 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.8 main, deb http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.9 main, deb-src http://apt.llvm.org/trusty/ llvm-toolchain-trusty-3.9 main"

- heroku config:set GH_TOKEN=""

- heroku config:set GH_REPO=""

- heroku buildpacks:add https://github.com/ivandeex/heroku-buildpack-apt

- heroku buildpacks:add https://github.com/heroku/heroku-buildpack-python
