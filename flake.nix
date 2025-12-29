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
        let
          # Script to extract text from a PDF using poppler's pdftotext
          # Usage: extract-pdf <path-to-pdf>
          extractPdf = pkgs.writeShellScriptBin "extract-pdf" ''
            if [ -z "$1" ]; then
              echo "Usage: extract-pdf <path-to-pdf>" >&2
              exit 1
            fi
            ${pkgs.poppler-utils}/bin/pdftotext "$1" -
          '';
        in
        {
          # Development shell with all required tools
          devShells.default = pkgs.mkShell {
            buildInputs = [
              pkgs.just           # Task runner (justfile)
              pkgs.jq             # JSON validation and manipulation
              pkgs.python3        # For local HTTP server (just serve)
              extractPdf          # Custom PDF text extraction tool
            ];
          };

          # Expose the extract-pdf script as a package
          packages.extract-pdf = extractPdf;
        };
    };
}
