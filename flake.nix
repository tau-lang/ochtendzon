{
    inputs = {
        nixpkgs.url = "github:nixos/nixpkgs/nixos-25.05";
        tau.url = "github:tau-lang/tau";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { nixpkgs, tau, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem(system:
    let
        pkgs = import nixpkgs {
            inherit system;
        };
        bi = [ tau.packages."${system}".default pkgs.gcc ];
    in
    {
        packages.default = pkgs.stdenv.mkDerivation {
            pname = "ochtendzon";
            version = "0.1.0";

            src = ./.;

            nativeBuildInputs = [
                pkgs.makeWrapper
            ];

            installPhase = ''
            mkdir -p $out/bin $out/share/man/man1
            cp ochtendzon $out/bin/
            cp man/ochtendzon.1 $out/share/man/man1/

            wrapProgram $out/bin/ochtendzon \
            --prefix PATH : ${pkgs.lib.makeBinPath bi}
            '';
        };
        devShells.default = pkgs.mkShell {
            buildInputs = bi;
        };
    });
}