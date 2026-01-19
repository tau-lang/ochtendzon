{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
    tau.url = "github:tau-lang/tau";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { nixpkgs, tau, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        lib = nixpkgs.lib;
        bi = [ tau.packages."${system}".default pkgs.gcc ];
      in {
        packages = rec {
          default = ochtendzon;

          ochtendzon = pkgs.stdenv.mkDerivation {
            pname = "ochtendzon";
            version = "0.1.0";

            src = ./.;

            nativeBuildInputs = [ pkgs.makeWrapper ];

            installPhase = ''
              mkdir -p $out/bin
              cp ochtendzon $out/bin/

              wrapProgram $out/bin/ochtendzon \
              --prefix PATH : ${pkgs.lib.makeBinPath bi}
            '';

            meta = {
              homepage = "https://github.com/tau-lang/ochtendzon";
              license = lib.licenses.eupl12;
              platforms = lib.platforms.all;
            };
          };

          ochtendzon-manpages = pkgs.stdenv.mkDerivation {
            pname = "ochtendzon-manpages";
            version = "0.1.0";

            src = ./.;

            installPhase = ''
              mkdir -p $out/share/man/man1
              cp man/ochtendzon.1 $out/share/man/man1/
            '';

            meta = {
              homepage = "https://github.com/tau-lang/ochtendzon";
              license = lib.licenses.eupl12;
              platforms = lib.platforms.all;
            };
          };
        };
        devShells.default =
          pkgs.mkShell { buildInputs = bi ++ [ pkgs.nixfmt ]; };
      });
}
