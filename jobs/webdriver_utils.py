"""Utility functions for webdriver setup and management"""
import os
import sys
import platform
import subprocess
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# Try to import various webdriver managers with fallbacks
try:
    from webdriver_manager.chrome import ChromeDriverManager
    webdriver_manager_available = True
except ImportError:
    webdriver_manager_available = False

try:
    import chromedriver_autoinstaller
    autoinstaller_available = True
except ImportError:
    autoinstaller_available = False


def get_chrome_version():
    """Get the installed Chrome/Chromium version"""
    system = platform.system()

    if system == "Windows":
        try:
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
            ]

            for path in chrome_paths:
                if os.path.exists(path):
                    try:
                        # FIX: make safe path first
                        safe_path = path.replace("\\", "\\\\")

                        cmd = [
                            "wmic",
                            "datafile",
                            "where",
                            f'name="{safe_path}"',
                            "get",
                            "Version",
                            "/value"
                        ]

                        output = subprocess.check_output(
                            cmd,
                            stderr=subprocess.STDOUT
                        )

                        version_str = output.decode("utf-8").strip()

                        if "Version=" in version_str:
                            version = version_str.split("=")[1].split(".")[0]
                            return version

                    except Exception:
                        try:
                            output = subprocess.check_output(
                                [path, "--version"],
                                stderr=subprocess.STDOUT
                            )

                            version = output.decode("utf-8").strip().split()[-1].split(".")[0]
                            return version

                        except Exception:
                            pass

        except Exception:
            pass

    else:
        # Linux / Mac
        try:
            for binary in [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser"
            ]:
                if os.path.exists(binary):

                    version = subprocess.check_output(
                        [binary, "--version"],
                        stderr=subprocess.STDOUT
                    )

                    version = version.decode("utf-8").strip().split()[-1].split(".")[0]
                    return version

        except Exception:
            pass

    # Default fallback
    return "120"


def run_setup_script():
    """Run the setup_chromedriver.py script"""

    try:
        script_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        setup_script = os.path.join(
            script_dir,
            "setup_chromedriver.py"
        )

        if os.path.exists(setup_script):

            st.info("Running chromedriver setup script...")

            result = subprocess.run(
                [sys.executable, setup_script],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:

                st.success("Chromedriver setup completed!")

                for line in result.stdout.split("\n"):

                    if "Chromedriver path:" in line:
                        return line.split("Chromedriver path:")[1].strip()

            else:
                st.warning(result.stderr)

        else:
            st.warning("Setup script not found")

    except Exception as e:
        st.warning(str(e))

    return None


def get_chromedriver_path():
    """Find chromedriver path"""

    system = platform.system()

    if system == "Windows":

        local_app_data = os.environ.get("LOCALAPPDATA", "")

        if local_app_data:

            path = os.path.join(
                local_app_data,
                "ChromeDriver",
                "chromedriver.exe"
            )

            if os.path.exists(path):
                return path

    else:

        home = os.path.expanduser("~")

        path = os.path.join(home, ".chromedriver", "chromedriver")

        if os.path.exists(path):
            return path

    return None


def setup_webdriver():
    """Setup Chrome WebDriver"""

    options = Options()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    # Method 1: Direct
    try:

        driver = webdriver.Chrome(options=options)

        st.success("Chrome started!")

        return driver

    except Exception:
        pass


    # Method 2: Existing chromedriver
    chromedriver_path = get_chromedriver_path()

    if chromedriver_path:

        try:

            service = Service(chromedriver_path)

            driver = webdriver.Chrome(
                service=service,
                options=options
            )

            return driver

        except Exception:
            pass


    # Method 3: webdriver-manager
    if webdriver_manager_available:

        try:

            service = Service(
                ChromeDriverManager().install()
            )

            driver = webdriver.Chrome(
                service=service,
                options=options
            )

            return driver

        except Exception:
            pass


    # Method 4: Manual paths
    system = platform.system()

    if system == "Windows":

        try:

            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
                )
            ]

            for path in chrome_paths:

                if os.path.exists(path):

                    options.binary_location = path

                    try:

                        driver = webdriver.Chrome(options=options)

                        return driver

                    except Exception:
                        continue

        except Exception:
            pass


    elif system == "Linux":

        try:

            options.binary_location = "/usr/bin/chromium"

            try:
                return webdriver.Chrome(options=options)
            except Exception:
                pass


            options.binary_location = "/usr/bin/google-chrome"

            try:
                return webdriver.Chrome(options=options)
            except Exception:
                pass

        except Exception:
            pass


    st.error("Failed to start Chrome WebDriver")

    return None
