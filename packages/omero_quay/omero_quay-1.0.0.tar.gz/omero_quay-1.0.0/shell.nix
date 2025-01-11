{ pkgs ? import <nixpkgs> {}}:
let
  fhs = pkgs.buildFHSUserEnv {
    name = "quay";

    targetPkgs = _: [
      pkgs.micromamba
      pkgs.python311
      pkgs.python311Packages.ipython
    ];

    profile = ''
      set -e
      eval "$(micromamba shell hook -s posix)"
      export MAMBA_ROOT_PREFIX=${builtins.getEnv "HOME"}/micromamba
      if [ -z "$MAMBA_ROOT_PREFIX/envs/quay" ]; then
        micromamba create -n quay -f environment.yml
      fi
      micromamba activate quay
      set +e
    '';
  };

in fhs.env
