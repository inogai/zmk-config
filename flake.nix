{
  description = "ZMK keyboard config development environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/release-25.11";

  outputs = {self, ...} @ inputs: let
    supportedSystems = [
      "x86_64-linux"
      "aarch64-linux"
      "x86_64-darwin"
      "aarch64-darwin"
    ];
    forEachSupportedSystem = f:
      inputs.nixpkgs.lib.genAttrs supportedSystems (
        system:
          f {
            pkgs = import inputs.nixpkgs {
              inherit system;
              overlays = [inputs.self.overlays.default];
            };
          }
      );
  in {
    overlays.default = final: prev: rec {
    };

    devShells = forEachSupportedSystem (
      {pkgs}: {
        default = pkgs.mkShellNoCC {
          packages = with pkgs; [
            just
            keymap-drawer
            # SVG to PNG conversion for layer images
            librsvg
            # Keyboard Layers App Companion deps
            hidapi
            (python313.withPackages (ps:
              with ps; [
                hid
                tenacity
                aiohttp
                zeroconf
                kivy
                # macOS transparent overlay
                pyobjc-core
                pyobjc-framework-Cocoa
                pyobjc-framework-Quartz
              ]))
          ];
        };
      }
    );
  };
}
