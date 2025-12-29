{
  description = "YMCA Schedule Management";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];

      perSystem = { pkgs, ... }:
        {
          # Development shell with required tools
          devShells.default = pkgs.mkShell {
            buildInputs = [
              pkgs.just           # Task runner (justfile)
              pkgs.jq             # JSON validation and manipulation
              pkgs.python3        # For local HTTP server (just serve)
            ];
          };
        };
    };
}
