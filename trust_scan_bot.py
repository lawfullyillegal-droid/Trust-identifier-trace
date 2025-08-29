def main():
    try:
        print("🔥 BOT STARTED")

        print("✅ Loading identifiers.yaml...")
        with open("identifiers.yaml", "r") as f:
            identifiers = yaml.safe_load(f)

        print("✅ Loading identity_profile.yaml...")
        with open("identity_profile.yaml", "r") as f:
            profile = yaml.safe_load(f)

        print("✅ Loading trust_overlay.xml...")
        with open("docs/trust_overlay.xml", "r") as f:
            overlay = f.read()

        print("✅ Writing output file...")
        os.makedirs("output", exist_ok=True)
        output_path = f"output/scan_log_{datetime.utcnow().isoformat()}Z.txt"
        with open(output_path, "w") as f:
            f.write("Scan complete.\n")
            f.write(f"Identifiers: {identifiers}\n")
            f.write(f"Profile: {profile}\n")
            f.write("Overlay loaded.\n")

        print("🔄 Committing output and overlay to GitHub...")
        os.system("git config --global user.name 'TrustBot'")
        os.system("git config --global user.email 'trustbot@localhost'")
        os.system("git add output/*.txt docs/overlay.html")
        os.system("git commit -m 'Auto-commit scan results'")
        os.system("git push https://x-access-token:${{ secrets.GH_TOKEN }}@github.com/${{ github.repository }} HEAD:main")

        print("✅ BOT COMPLETED")

    except Exception as e:
        print(f"❌ BOT FAILED: {e}")
