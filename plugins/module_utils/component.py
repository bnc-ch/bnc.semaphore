from __future__ import absolute_import, division, print_function

try:
    import requests
except ImportError as e:
    MISSING_LIBRARY = "requests"
    MISSING_LIBRARY_E = e

try:
    from yarl import URL
except ImportError as e:
    MISSING_LIBRARY = "yarl"
    MISSING_LIBRARY_E = e

from ansible.module_utils.basic import missing_required_lib


# pylint: disable=invalid-name
__metaclass__ = type


class SemaphoreComponent:

    # API attributes
    attrs = {"name": str}

    # Expected state of the component
    state = "present"

    # Base URL of Semaphore API
    __url: str

    # URL path for component
    __path: str

    # Auth token for API
    __token: str

    # Constructor
    def __init__(self, module):

        # Missing libraries
        if MISSING_LIBRARY:
            module.fail_json(
                msg=missing_required_lib(MISSING_LIBRARY), exception=MISSING_LIBRARY_E
            )

        # Save module
        self.module = module

        # Extract parameters
        self.__url = module.params.get("url")
        self.__token = module.params.get("token")
        self.state = module.params.get("state")

        # Extract attributes
        for key in self.attrs.keys():
            self.attrs[key] = module.params.get(key)

    # Get list of components from Semaphore
    def get_components(self):

        # Component URL
        url = URL(self.__url) / self.__path

        # Perform request
        try:
            ret = requests.get(url, headers={"Authorization": f"Bearer {self.__token}"})
        except requests.RequestException as e:
            self.module.fail_json(
                changed=False, msg=f"An error occured while performing the request: {e}"
            )

        # Check result
        if ret.status_code not in [200]:
            self.module.fail_json(
                changed=False,
                msg=f"Unexpected response code {ret.status_code} from server. Response was: {ret.text}",
            )

        # Read result
        try:
            components = ret.json()
        except requests.RequestException as e:
            self.module.fail_json(changed=False, msg=f"Cannot read returned JSON: {e}")

        # Return
        return components

    # Search for component in list
    def get_component(self, name):

        # Get list of existing components
        components = self.get_components()

        # Search by ID
        return next((x for x in components if x["name"] == name), None)

    # Create or update component
    def create_or_update(self):

        # Component URL
        url = URL(self.__url) / self.__path

        # Check for existing component by name
        component = self.get_component(self.attrs["name"])

        # Catch requests exceptions
        try:

            # If component already exist, we try to update
            if component:

                # Prepare URL
                url = url / component["id"]

                # Prepare attributes
                self.attrs["id"] = component["id"]

                # Make PUT request
                ret = requests.put(
                    url,
                    json=self.attrs,
                    headers={"Authorization": f"Bearer {self.__token}"},
                )

                # Check result
                if ret.status_code not in [204]:
                    self.module.fail_json(
                        changed=False,
                        msg=f"Unexpected response code {ret.status_code} from server. Response was: {ret.text}",
                    )

                # Update component
                component = self.get_component(component["name"])

                # Return
                self.module.exit_json(changed=True, result=component)

            # If not, we create
            else:

                # Make POST request
                ret = requests.post(
                    url,
                    json=self.attrs,
                    headers={"Authorization": f"Bearer {self.__token}"},
                )

                # Check result
                if ret.status_code not in [201]:
                    self.module.fail_json(
                        changed=False,
                        msg=f"Unexpected response code {ret.status_code} from server. Response was: {ret.text}",
                    )

                # Read result
                try:
                    component = ret.json()
                except requests.RequestException as e:
                    self.module.fail_json(
                        changed=False, msg=f"Cannot read returned JSON: {e}"
                    )

                # Return
                self.module.exit_json(changed=True, result=component)

        except requests.RequestException as e:
            self.module.fail_json(
                changed=False, msg=f"An error occured while performing the request: {e}"
            )

    # Ensure component does not exist
    def ensure_removed(self):

        # Check if component exists
        component = self.get_component(self.attrs["name"])
        if not component:
            return self.module.exit_json(changed=False)

        # Component URL
        url = URL(self.__url) / self.__path / component["id"]

        # Catch requests exceptions
        try:

            # Make DELETE request
            ret = requests.delete(
                url, headers={"Authorization": f"Bearer {self.__token}"}
            )

            # Check result
            if ret.status_code not in [204]:
                self.module.fail_json(
                    changed=False,
                    msg=f"Unexpected response code {ret.status_code} from server. Response was: {ret.text}",
                )

            # Return
            self.module.exit_json(changed=True)

        except requests.RequestException as e:
            self.module.fail_json(
                changed=False, msg=f"An error occured while performing the request: {e}"
            )


class SemaphoreProjectComponent(SemaphoreComponent):

    # API attributes
    attrs = SemaphoreComponent.attrs | {"project_id": int}

    # Constructor
    def __init__(self, module):
        super().__init__(module)

        # Update path
        self.__path = f"/project/{self.attrs.project_id}{self.__path}"