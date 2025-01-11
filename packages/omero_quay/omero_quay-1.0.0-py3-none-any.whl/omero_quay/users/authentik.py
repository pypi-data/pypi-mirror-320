from __future__ import annotations

import logging
import os

import authentik_client

from ..core.manifest import User

log = logging.getLogger(__name__)


MIN_UID = 2000


def get_users(instance: str) -> list[User]:
    # Configure Bearer authorization: authentik
    configuration = authentik_client.Configuration(
        access_token=os.environ["AUTHENTIK_TOKEN"],
        host="https://auth.omero-fbi.fr/api/v3",
    )

    # Enter a context with an instance of the API client
    with authentik_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = authentik_client.CoreApi(api_client)
        response = api_instance.core_users_list(groups_by_name=[instance])
        atk_users = response.results

    institution_mapping = {
        "{UAI}0442953W": "Nantes Université",
        "{CNRS}UAR3556": "UAR BioCore",
        "{UNIV MONTPELLIER}UAR3426": "UAR BioCampus",
        "{CNRS}UMR5297": "LIRMM",
    }

    quay_users = []

    for atk_user in atk_users:
        if not atk_user.attributes:
            log.info("user %s has no attributes", atk_user.username)
            continue
        if est := atk_user.attributes.get("supannEtablissement"):
            institution = institution_mapping.get(est)
        else:
            institution = None
        quay_user = User(
            id=atk_user.uid,
            name=atk_user.username,
            last_name=atk_user.attributes.get("sn", atk_user.name.split(" ")[-1]),
            first_name=atk_user.attributes.get(
                "givenName", atk_user.name.split(" ")[0]
            ),
            email=atk_user.email,
            institution=institution,
            unix_uid=(atk_user.pk + MIN_UID),
            unix_gid=(atk_user.pk + MIN_UID),
        )
        quay_users.append(quay_user)

    return quay_users
