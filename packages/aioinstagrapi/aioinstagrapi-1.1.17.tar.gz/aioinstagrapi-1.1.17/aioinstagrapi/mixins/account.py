from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Dict

from aioinstagrapi.exceptions import ClientError, ClientLoginRequired
from aioinstagrapi.extractors import extract_account, extract_user_short
from aioinstagrapi.models import Account, UserShort
from aioinstagrapi.utils import dumps, gen_token


class AccountMixin:
    """
    Helper class to manage your account
    """


    async def account_info(self) -> Account:
        """
        Fetch your account info

        Returns
        -------
        Account
            An object of Account class
        """
        result = await self.private_request("accounts/current_user/?edit=true")
        return extract_account(result["user"])

    async def set_external_url(self, external_url) -> dict:
        """
        Set new biography
        """

        signed_body = f"signed_body=SIGNATURE.%7B%22updated_links%22%3A%22%5B%7B%5C%22url%5C%22%3A%5C%22{external_url}%5C%22%2C%5C%22title%5C%22%3A%5C%22%5C%22%2C%5C%22link_type%5C%22%3A%5C%22external%5C%22%7D%5D%22%2C%22_uid%22%3A%22{self.user_id}%22%2C%22_uuid%22%3A%22{self.uuid}%22%7D"
        return await self.private_request(
            "accounts/update_bio_links/", data=signed_body, with_signature=False
        )

    async def account_set_private(self) -> bool:
        """
        Sets your account private

        Returns
        -------
        Account
            An object of Account class
        """
        assert self.user_id, "Login required"
        user_id = str(self.user_id)
        data = self.with_action_data({"_uid": user_id, "_uuid": self.uuid})
        result = await self.private_request("accounts/set_private/", data)
        return result["status"] == "ok"

    async def account_set_public(self) -> bool:
        """
        Sets your account public

        Returns
        -------
        Account
            An object of Account class
        """
        assert self.user_id, "Login required"
        user_id = str(self.user_id)
        data = self.with_action_data({"_uid": user_id, "_uuid": self.uuid})
        result = await self.private_request("accounts/set_public/", data)
        return result["status"] == "ok"

    async def account_security_info(self) -> dict:
        """
        Fetch your account security info

        Returns
        -------
        dict
            Contains useful information on security settings: {
            "is_phone_confirmed": true,
            "is_two_factor_enabled": false,
            "is_totp_two_factor_enabled": true,
            "is_trusted_notifications_enabled": true,
            "is_eligible_for_whatsapp_two_factor": true,
            "is_whatsapp_two_factor_enabled": false,
            "backup_codes": [...],
            "trusted_devices": [],
            "has_reachable_email": true,
            "eligible_for_trusted_notifications": true,
            "is_eligible_for_multiple_totp": false,
            "totp_seeds": [],
            "can_add_additional_totp_seed": false
            }
        """
        return await self.private_request(
            "accounts/account_security_info/", self.with_default_data({})
        )

    async def account_edit(self, **data: Dict) -> Account:
        """
        Edit your profile (authorized account)

        Parameters
        ----------
        data: Dict
            Fields you want to edit in your account as key and value pairs

        Returns
        -------
        Account
            An object of Account class
        """
        fields = (
            "external_url",
            "username",
            "full_name",
            "biography",
            "phone_number",
            "email",
        )
        # if "email" in data:
        #     # email is handled separately
        #     self.send_confirm_email(data.pop("email"))
        # if "phone_number" in data:
        #     # phone_number is handled separately
        #     self.send_confirm_phone_number(data.pop("phone_number"))
        data = {key: val for key, val in data.items() if key in fields}
        if "email" not in data or "phone_number" not in data:
            # Instagram Error: You need an email or confirmed phone number.
            user_data = self.account_info().dict()
            user_data = {field: user_data[field] for field in fields}
            data = dict(user_data, **data)
        full_name = data.pop("full_name", None)
        if full_name:
            # Instagram original field-name for full user name is "first_name"
            data["first_name"] = full_name
        # Biography with entities (markup)
        result = await self.private_request(
            "accounts/edit_profile/", self.with_default_data(data)
        )
        biography = data.get("biography")
        if biography:
            self.account_set_biography(biography)
        return extract_account(result["user"])

    async def account_set_biography(self, biography: str) -> bool:
        """
        Set biography with entities (markup)

        Parameters
        ----------
        biography: str
            Biography raw text

        Returns
        -------
        bool
            A boolean value
        """
        data = {"logged_in_uids": dumps([str(self.user_id)]), "raw_text": biography}
        result = await self.private_request(
            "accounts/set_biography/", self.with_default_data(data)
        )
        return result["status"] == "ok"

    async def account_change_picture(self, path: Path) -> UserShort:
        """
        Change photo for your profile (authorized account)

        Parameters
        ----------
        path: Path
            Path to the image you want to update as your profile picture

        Returns
        -------
        UserShort
            An object of UserShort class
        """
        upload_id, _, _ = await self.photo_rupload(Path(path))
        result = await self.private_request(
            "accounts/change_profile_picture/",
            self.with_default_data({"use_fbuploader": True, "upload_id": upload_id}),
        )
        return extract_user_short(result["user"])

    async def news_inbox_v1(self, mark_as_seen: bool = False) -> dict:
        """
        Get old and new stories as is

        Parameters
        ----------
        mark_as_seen: bool
            Mark as seen or not

        Returns
        -------
        dict
        """
        return await self.private_request(
            "news/inbox/", params={"mark_as_seen": mark_as_seen}
        )

    async def send_confirm_email(self, email: str) -> dict:
        """
        Send confirmation code to new email address

        Parameters
        ----------
        email: str
            Email address

        Returns
        -------
        dict
        """
        return await self.private_request(
            "accounts/send_confirm_email/",
            self.with_extra_data(
                {"send_source": "personal_information", "email": email}
            ),
        )

    async def send_confirm_phone_number(self, phone_number: str) -> dict:
        """
        Send confirmation code to new phone number

        Parameters
        ----------
        phone_number: str
            Phone number

        Returns
        -------
        dict
        """
        return await self.private_request(
            "accounts/initiate_phone_number_confirmation/",
            self.with_extra_data(
                {
                    "android_build_type": "release",
                    "send_source": "edit_profile",
                    "phone_number": phone_number,
                }
            ),
        )
