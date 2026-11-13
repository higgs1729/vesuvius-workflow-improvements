# Build and reproduce

Use Linux or the Linux filesystem of WSL so CMake can create its reader header symlink. Set KIT to the absolute path of the extracted supplement, VILLA to an upstream checkout with the fixed commit, and SOURCE and BUILD to fresh paths.

~~~sh
FIXED=14d4e725df8b569e6fc8ceb3c04d130f705c1565
git -C "$VILLA" -c core.autocrlf=false -c core.eol=lf worktree add --detach "$SOURCE" "$FIXED"
cd "$SOURCE"
for patch in 01-pack-components.patch 02-preserve-grid.patch 03-R009.patch 04-R007.patch
do
    git -c core.autocrlf=false -c core.eol=lf apply --check --whitespace=warn "$KIT/patches/$patch" || exit
    git -c core.autocrlf=false -c core.eol=lf apply --whitespace=warn "$KIT/patches/$patch" || exit
done
~~~

The second patch carries one trailing space from a logging line. Keep the supplied patch bytes and LF source files for hash comparison. [Ten expected source hashes and patch order](SOURCE_HASHES.json) · [Fixed upstream tree](https://github.com/ScrollPrize/villa/tree/14d4e725df8b569e6fc8ceb3c04d130f705c1565)

## Configure and build

Follow the upstream instructions for dependencies. The recorded run used already available Ubuntu dependencies, local PaStiX/SPM, libigl and vc_delta3d sources with FetchContent disconnected, and the upstream libbacktrace ExternalProject supplied by a local Git mirror at 0b9b49cf4a2c9229fc052d6716e1528b2f23e91a. The command below shows the CPU options and standard targets. [Fixed build instructions](https://github.com/ScrollPrize/villa/blob/14d4e725df8b569e6fc8ceb3c04d130f705c1565/volume-cartographer/README.md)

~~~sh
cmake -S "$SOURCE/volume-cartographer" -B "$BUILD" -G Ninja \
  -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_Fortran_COMPILER=gfortran \
  -DCMAKE_BUILD_TYPE=QuickBuild -DVC_QUICKBUILD_OPT_LEVEL=0 \
  -DBUILD_SHARED_LIBS=ON -DVC_BUILD_FLATBOI=ON -DVC_BUILD_APPS=ON \
  -DVC_TESTING=OFF -DFLATBOI_BUILD_SLIM_TESTS=OFF -DVC_BUILD_FIBERLETS=OFF \
  -DVC_BUILD_PYTHON=OFF -DVC_READER_ENABLE_CUDA=OFF -DVC_OBJECT_STORE_BUILD_SERVER=OFF
cmake --build "$BUILD" --parallel 1 --target flatboi vc_core vc_obj2tifxyz vc_render_tifxyz
~~~

Build UvGridRasterizer and its callers from the same patched header and keep the resulting binaries and shared libraries together. The class layout changes. R150 linked two patched translation units in an isolated ELF. R159 built shared libraries on 7ad02f4. R160 built and exercised the new shared libraries on 14d4e725.

## Native run conditions

The recorded runs used one allowed CPU, one OpenMP and numerical thread, a 4 GiB address-space limit, disabled core dumps and network isolation after inputs were staged. Use an available CPU from your process affinity mask.

~~~sh
export OMP_NUM_THREADS=1 OMP_THREAD_LIMIT=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PASTIX_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OPENCV_FOR_THREADS_NUM=1
ulimit -v 4194304
ulimit -c 0
# Run the commands below inside a shell pinned with taskset -c "$CPU".
~~~

## R005 · Flatten a surface

Set SEG to one local surface from the input manifests and use fresh output paths. Packing is off by default. The two packing flags are mutually exclusive.

~~~sh
"$BUILD/bin/flatboi" "$SEG" --output="$DEFAULT_OUT" --keep=100 5
"$BUILD/bin/flatboi" "$SEG" --output="$LEGACY_OUT" --keep=100 5 --pack-components
"$BUILD/bin/flatboi" "$SEG" --output="$GRID_OUT" --keep=100 5 --pack-components-preserve-grid
~~~

The integrated run used the first PHerc0814 surface. The separate low-retention run used the same surface with --keep=1.5 and five iterations. The result extracts give expected integrated XYZ hashes and scale. [Inputs](DATA.md) · [Results](RESULTS.json)

## R007 · Check crop parsing

Run the saved CLI suite on the rebuilt renderer. It uses absent fixture paths to check which settings reach input opening and needs no CT.

~~~sh
python3 -B "$KIT/checks/check_crop_cli.py" "$BUILD/bin/vc_render_tifxyz"
~~~

## R009 · Compare normal and resumed Zarr output

Set W035 to the PHerc0139 surface, VOLUME to its local sparse CT cache, and NORMAL, FRESH and PARTIAL to separate unused paths. The partial case copies level 0 from the normal output to test missing pyramid initialization. [Inputs and cache layout](DATA.md)

~~~sh
render() {
  "$BUILD/bin/vc_render_tifxyz" --volume "$VOLUME" --segmentation "$W035" \
    --zarr-compressor none --pyramid true --scale 1 --group-idx 0 --num-slices 28 \
    --slice-step 1 --surface-interpolation bicubic --voxel-size 9.362 --voxel-unit micrometer \
    --cache-gb 1 --flip-normals --crop-x 2239 --crop-y 1343 --crop-width 1 --crop-height 129 "$@"
}
render --zarr-output "$NORMAL"
render --zarr-output "$FRESH" --resume
mkdir "$PARTIAL"
cp -a "$NORMAL/.zgroup" "$NORMAL/0" "$PARTIAL/"
render --zarr-output "$PARTIAL" --resume
diff -qr "$NORMAL" "$FRESH"
diff -qr "$NORMAL" "$PARTIAL"
~~~

Compare logical arrays in ZYX order using each .zarray's shape and chunks. The final level-0 chunk stores one logical row per layer and 3,556 zero padding bytes. Measure SHA, mtime_ns and inode on the same partial copy before and after resume to check retention. [Expected logical hashes](RESULTS.json)

The small local Python check needs a patched vc_reader installation or matching real _reader and _catalog extensions plus the patched wrapper. It needs no CT. The integrated native build disables Python. The earlier Python runtime check used isolated imports. [Check and options](checks/check_zarr_python.py)

~~~sh
python3 -B "$KIT/checks/check_zarr_python.py" --help
~~~
