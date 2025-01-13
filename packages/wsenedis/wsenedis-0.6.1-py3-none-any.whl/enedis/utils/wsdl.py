from importlib.resources import files, as_file


def load_services():
    services = {}
    # List of WSDL files, manually specified
    wsdl_files = {
        files('enedis.ressources.Services.RecherchePoint'): 'RecherchePoint-v2.0.wsdl',
        files('enedis.ressources.Services.CommandeArretServiceSouscritMesures'): 'CommandeArretServiceSouscritMesures-v1.0.wsdl',
        files('enedis.ressources.Services.ConsultationPoint'): 'ConsultationPoint-v4.0.wsdl',
        files('enedis.ressources.Services.ConsultationDonneesTechniquesContractuelles'): 'ConsultationDonneesTechniquesContractuelles-v1.0.wsdl',
        files('enedis.ressources.Services.ConsultationMesures'): 'ConsultationMesures-v1.1.wsdl',
        files('enedis.ressources.Services.M023'): 'B2B_M023ITC.wsdl',
        files('enedis.ressources.Services.M023'): 'B2B_M023MFI.wsdl',
        files('enedis.ressources.Services.M023'): 'B2B_M023MFA.wsdl',
        files('enedis.ressources.Services.RechercheServicesSouscritsMesures'): 'RechercheServicesSouscritsMesures.wsdl',
        files('enedis.ressources.Services.CommanderAccesDonneesMesures'): 'CommanderAccesDonneesMesures-V1.0.wsdl',
        files('enedis.ressources.Services.CommandeCollectePublicationMesures'): 'CommandeCollectePublicationMesures-v3.0.wsdl',
        files('enedis.ressources.Services.ConsultationMesuresDetaillees'): 'ADAM.ConsulterMesuresServiceReadV3.wsdl',
    }

    for resources_path, wsdl_file in wsdl_files.items():
        with as_file(resources_path.joinpath(wsdl_file)) as path:
            services[path.stem] = path.as_posix()

    return services

SERVICES = load_services()

def wsdl(service_name: str) -> str:
    """Return path to WSDL file for `service_name`."""
    try:
        return SERVICES[service_name]
    except KeyError:
        raise KeyError(
            "Unknown service name {!r}, available services are {}".format(
                service_name,
                ", ".join(sorted(SERVICES)),
            ),
        ) from None


