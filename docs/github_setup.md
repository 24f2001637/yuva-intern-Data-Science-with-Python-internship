# Upload this project to GitHub

Suggested name: **data-science-internship**.

Create an empty repository in your GitHub account. Choose public visibility if the internship evaluator needs access without an invitation; otherwise choose private and grant the evaluator access. For a Git push workflow, leave the remote repository empty: do not initialise it with a README, license or gitignore because this project already has files.

Extract the ZIP and open a terminal in `internship-data-science`, then run:

```bash
git init -b main
git add .
git commit -m "Add internship reports and reproducible analysis for weeks 1 to 3"
git remote add origin https://github.com/YOUR_USERNAME/data-science-internship.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. If Git asks for your name or email, configure your own identity before committing. Authenticate using GitHub's supported sign-in flow or a credential manager; never paste credentials into project files.

Alternatively, use GitHub's Upload files interface to upload the extracted project contents. Upload the contents rather than the ZIP itself so the README, reports and code are browsable. Ensure hidden `.github`, `.gitignore` and `.gitattributes` files are included; the command-line method is more reliable for these.

After publication, open the repository and check that the README displays, its report links work, and the Actions workflow completes. The workflow definition is provided; no hosted CI run is claimed until GitHub executes it. Submit the repository URL in the internship portal's GitHub field.

Official GitHub guide: https://docs.github.com/en/repositories/creating-and-managing-repositories/quickstart-for-repositories
