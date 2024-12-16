from defusedxml import xmlrpc
from django.conf import settings

xmlrpc.monkey_patch()

import xmlrpc.client  # noqa: E402 # nosec


def authenticate():
    common = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(settings.ODOO_DB, settings.ODOO_USERNAME, settings.ODOO_PASSWORD, {})
    if not uid:
        raise Exception("Authentication failed with Odoo")
    return uid


def is_odoo_config_valid():
    """Validate Odoo configuration settings."""
    required_fields = [
        settings.ODOO_URL,
        settings.ODOO_DB,
        settings.ODOO_USERNAME,
        settings.ODOO_PASSWORD,
        settings.ODOO_MAILING_LIST_ID,
    ]
    return all(required_fields)


def subscribe_user_to_news(user_email: str, user_name: str):
    if not is_odoo_config_valid():
        print("Odoo configuration is invalid. Skipping subscription.")
        return

    uid = authenticate()
    models = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")

    # Check if the contact already exists in Odoo
    contact_ids = models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_PASSWORD,
        "mailing.contact",
        "search",
        [[("email", "=", user_email)]],
    )

    if not contact_ids:
        # Create a new contact if it doesn't exist
        contact_data = {
            "name": user_name if user_name else user_email,  # Use name if provided, fallback to email
            "email": user_email,
        }
        contact_id = models.execute_kw(
            settings.ODOO_DB,
            uid,
            settings.ODOO_PASSWORD,
            "mailing.contact",
            "create",
            [contact_data],
        )
        print(f"New user created with ID {contact_id}")
    else:
        contact_id = contact_ids[0]
        print(f"User exists with ID {contact_id}")

    # Check if the user is subscribed to the specific mailing list
    subscription_ids = models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_PASSWORD,
        "mailing.contact.subscription",
        "search",
        [
            [
                ("contact_id", "=", contact_id),
                ("list_id", "=", settings.ODOO_MAILING_LIST_ID),
            ]
        ],
    )

    if not subscription_ids:
        # Subscribe the user to the mailing list
        subscription_data = {
            "contact_id": contact_id,
            "list_id": settings.ODOO_MAILING_LIST_ID,
            "opt_out": False,
        }
        subscription_id = models.execute_kw(
            settings.ODOO_DB,
            uid,
            settings.ODOO_PASSWORD,
            "mailing.contact.subscription",
            "create",
            [subscription_data],
        )
        print(f"User subscribed to mailing list with subscription ID {subscription_id}")
    else:
        # Update the existing subscription to ensure opt_out is False
        models.execute_kw(
            settings.ODOO_DB,
            uid,
            settings.ODOO_PASSWORD,
            "mailing.contact.subscription",
            "write",
            [subscription_ids, {"opt_out": False}],
        )
        print(f"User's subscription updated to opt-in for mailing list {settings.ODOO_MAILING_LIST_ID}")


def unsubscribe_user_from_news(user_email: str):
    if not is_odoo_config_valid():
        print("Odoo configuration is invalid. Skipping subscription.")
        return
    uid = authenticate()
    models = xmlrpc.client.ServerProxy(f"{settings.ODOO_URL}/xmlrpc/2/object")

    # Find the contact by email
    contact_ids = models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_PASSWORD,
        "mailing.contact",
        "search",
        [[("email", "=", user_email)]],
    )

    if not contact_ids:
        print(f"No contact found for email {user_email} to unsubscribe")
        return

    contact_id = contact_ids[0]

    # Find the subscription for the specific mailing list
    subscription_ids = models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_PASSWORD,
        "mailing.contact.subscription",
        "search",
        [
            [
                ("contact_id", "=", contact_id),
                ("list_id", "=", settings.ODOO_MAILING_LIST_ID),
            ]
        ],
    )

    if not subscription_ids:
        print(f"No subscription found for contact {contact_id} to mailing list {settings.ODOO_MAILING_LIST_ID}")
        return

    # Update the subscription to set opt_out to True
    models.execute_kw(
        settings.ODOO_DB,
        uid,
        settings.ODOO_PASSWORD,
        "mailing.contact.subscription",
        "write",
        [subscription_ids, {"opt_out": True}],
    )

    print(f"User {user_email} has been unsubscribed from mailing list {settings.ODOO_MAILING_LIST_ID}")
