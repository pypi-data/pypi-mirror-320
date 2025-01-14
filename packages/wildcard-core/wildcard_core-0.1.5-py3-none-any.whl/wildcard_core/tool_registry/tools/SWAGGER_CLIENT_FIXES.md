# Fixing Swagger Client Package Installation Issues

## Problem Identification
- Generated swagger clients have naming conflicts between package namespace and internal modules
- Packages install a generic `swagger_client` module alongside specific modules
- This causes import conflicts and `ModuleNotFoundError` issues

## Solution Steps
1. Modify `setup.py` files to explicitly specify package namespaces
2. Remove generic `swagger_client` package from installation
3. Ensure all imports use the specific client namespace (e.g., `gmail_swagger_client` or `airtable_swagger_client`)

## Key Changes
- Update package list in `setup.py` to only include namespaced packages
- Set `package_dir` to map the correct package namespace
- Reinstall packages after changes

## Template for Future Package Fixes

When fixing swagger-generated client packages:

### 1. Check setup.py configuration
- Replace `find_packages()` with explicit package list
- Use namespaced package names (e.g., "[package_name]_swagger_client")
- Include all necessary subpackages (.api, .models)
- Set package_dir to map the namespace correctly

### 2. Example setup.py structure
```python
setup(
    name="[package-name]-swagger-client",
    version="1.0.0",
    packages=[
        "[package_name]_swagger_client",
        "[package_name]_swagger_client.api",
        "[package_name]_swagger_client.models"
    ],
    package_dir={
        "[package_name]_swagger_client": "[package_name]_swagger_client"
    }
)
```

### 3. Installation steps
```bash
# Uninstall existing package
pip uninstall -y [package-name]-swagger-client

# Install modified package
cd path/to/package
python setup.py install
```

### 4. Verification
- Check installed egg file contents
- Verify no generic `swagger_client` module is present
- Test imports using the specific namespace
- Ensure no naming conflicts with other installed packages

## Important Notes
- Always use the specific client namespace in imports
- Avoid generic `swagger_client` namespace
- Keep package names consistent throughout the codebase
- When generating new swagger clients, immediately update the setup.py before installing 