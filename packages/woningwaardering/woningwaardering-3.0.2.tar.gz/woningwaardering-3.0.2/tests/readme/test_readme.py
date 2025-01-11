import json
from datetime import date

from tests.utils import assert_output_model
from woningwaardering import Woningwaardering
from woningwaardering.vera.bvg.generated import (
    BouwkundigElementenBouwkundigElement,
    EenhedenAdresBasis,
    EenhedenAdresseerbaarObjectBasisregistratie,
    EenhedenEenheid,
    EenhedenEnergieprestatie,
    EenhedenPand,
    EenhedenRuimte,
    EenhedenWoonplaats,
    EenhedenWozEenheid,
    WoningwaarderingResultatenWoningwaarderingResultaat,
)
from woningwaardering.vera.referentiedata import (
    Bouwkundigelementdetailsoort,
    Bouwkundigelementsoort,
    Energielabel,
    Energieprestatiesoort,
    Energieprestatiestatus,
    Pandsoort,
    Ruimtedetailsoort,
    Ruimtesoort,
    Woningwaarderingstelsel,
)


def test_readme_python_voorbeeld():
    # Dit is voorbeeld 2 uit de readme met als input een Python object.
    wws = Woningwaardering(peildatum=date(2025, 1, 1))

    eenheid = EenhedenEenheid(
        id="37101000032",
        bouwjaar=1924,
        woningwaarderingstelsel=Woningwaarderingstelsel.zelfstandige_woonruimten,
        adres=EenhedenAdresBasis(
            straatnaam="Nieuwe Boezemstraat",
            huisnummer="27",
            huisnummer_toevoeging="",
            postcode="3034PH",
            woonplaats=EenhedenWoonplaats(naam="ROTTERDAM"),
        ),
        adresseerbaarObjectBasisregistratie=EenhedenAdresseerbaarObjectBasisregistratie(
            id="0599010000485697", bagIdentificatie="0599010000485697"
        ),
        panden=[
            EenhedenPand(
                soort=Pandsoort.eengezinswoning,
            )
        ],
        woz_eenheden=[
            EenhedenWozEenheid(
                waardepeildatum=date(2022, 1, 1), vastgesteldeWaarde=618000
            ),
            EenhedenWozEenheid(
                waardepeildatum=date(2023, 1, 1), vastgesteldeWaarde=643000
            ),
        ],
        energieprestaties=[
            EenhedenEnergieprestatie(
                soort=Energieprestatiesoort.energie_index,
                status=Energieprestatiestatus.definitief,
                begindatum=date(2019, 2, 25),
                einddatum=date(2029, 2, 25),
                registratiedatum="2019-02-26T14:51:38+01:00",
                label=Energielabel.c,
                waarde="1.58",
            )
        ],
        gebruiksoppervlakte=187,
        monumenten=[],
        ruimten=[
            EenhedenRuimte(
                id="Space_108014589",
                soort=Ruimtesoort.vertrek,
                detailSoort=Ruimtedetailsoort.slaapkamer,
                naam="Slaapkamer",
                inhoud=60.4048,
                oppervlakte=21.047,
                verwarmd=True,
                gemeenschappelijk=True,
            ),
            EenhedenRuimte(
                id="Space_108006229",
                soort=Ruimtesoort.vertrek,
                detailSoort=Ruimtedetailsoort.keuken,
                naam="Keuken",
                inhoud=57.4359,
                oppervlakte=20.3673,
                verwarmd=True,
                gemeenschappelijk=True,
                bouwkundigeElementen=[
                    BouwkundigElementenBouwkundigElement(
                        id="Aanrecht_108006231",
                        id_bimmodel="3ZBiDoTKz0JfnjhzfVcYcF",
                        naam="Aanrecht",
                        omschrijving="Aanrecht in Keuken",
                        soort=Bouwkundigelementsoort.voorziening,
                        detailSoort=Bouwkundigelementdetailsoort.aanrecht,
                        lengte=2700,
                    )
                ],
            ),
        ],
    )

    woningwaardering_resultaat = wws.waardeer(eenheid)
    with open("tests/readme/output_json_python_voorbeeld.json", "r") as f:
        expected_result = (
            WoningwaarderingResultatenWoningwaarderingResultaat.model_validate(
                json.load(f)
            )
        )
        assert_output_model(woningwaardering_resultaat, expected_result)


def test_readme_json_voorbeeld():
    # Dit is voorbeeld 1 uit de readme met als input een JSON bestand.
    wws = Woningwaardering(peildatum=date(2025, 1, 1))
    with open(
        "tests/data/generiek/input/37101000032.json",
        "r+",
    ) as file:
        eenheid = EenhedenEenheid.model_validate_json(file.read())
        woningwaardering_resultaat = wws.waardeer(eenheid)
        with open("tests/readme/output_json_json_voorbeeld.json", "r") as f:
            expected_result = (
                WoningwaarderingResultatenWoningwaarderingResultaat.model_validate(
                    json.load(f)
                )
            )
            assert_output_model(woningwaardering_resultaat, expected_result)
