{
  pkgs ? import <nixpkgs> {},
  keyring ? pkgs.python38Packages.keyring,
}:
pkgs.poetry2nix.mkPoetryEnv {
  projectDir = ./.;
  overrides = pkgs.poetry2nix.overrides.withDefaults (
    self: super: {
      keyring = keyring;
    }
  );
}
