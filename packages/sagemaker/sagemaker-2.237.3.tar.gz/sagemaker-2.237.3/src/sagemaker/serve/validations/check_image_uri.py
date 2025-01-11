"""Validates that a given image_uri is not a 1p image."""

from __future__ import absolute_import

# Generated by running the parse_registry_accounts.py script
all_accounts = {
    "495149712605",
    "671472414489",
    "390048526115",
    "440796970383",
    "740489534195",
    "777275614652",
    "774647643957",
    "765400339828",
    "644912444149",
    "309385258863",
    "250201462417",
    "895741380848",
    "649008135260",
    "457447274322",
    "836785723513",
    "510948584623",
    "377024640650",
    "662702820516",
    "121021644041",
    "376037874950",
    "515509971035",
    "834264404009",
    "205585389593",
    "557239378090",
    "167761179201",
    "615547856133",
    "941853720454",
    "492215442770",
    "098760798382",
    "464438896020",
    "450853457545",
    "414596584902",
    "675030665977",
    "017069133835",
    "387376663083",
    "131013547314",
    "341593696636",
    "131546521161",
    "102112518831",
    "926135532090",
    "246618743249",
    "867004704886",
    "433757028032",
    "802834080501",
    "281123927165",
    "966458181534",
    "453252182341",
    "106583098589",
    "651117190479",
    "226302683700",
    "275950707576",
    "314341159256",
    "913387583493",
    "415577184552",
    "297031611018",
    "522234722520",
    "783357654285",
    "563025443158",
    "680994064768",
    "236514542706",
    "744548109606",
    "406833011540",
    "972752614525",
    "447278800020",
    "024640144536",
    "341280168497",
    "324986816169",
    "720646828776",
    "906073651304",
    "566113047672",
    "835444307964",
    "578805364391",
    "246785580436",
    "936697816551",
    "404615174143",
    "929884845733",
    "380420809688",
    "205493899709",
    "429704687514",
    "462105765813",
    "759080221371",
    "406031935815",
    "712779665605",
    "890145073186",
    "469771592824",
    "089933028263",
    "054986407534",
    "446045086412",
    "479947661362",
    "094389454867",
    "664544806723",
    "492261229750",
    "763104351884",
    "438346466558",
    "912233562940",
    "904829902805",
    "440695851116",
    "422961961927",
    "488287956546",
    "245909111842",
    "468650794304",
    "301217895009",
    "520713654638",
    "658757709296",
    "685385470294",
    "424196993095",
    "119527597002",
    "559312083959",
    "141502667606",
    "271483468897",
    "632365934929",
    "855470959533",
    "836651553127",
    "364406365360",
    "750251592176",
    "286214385809",
    "860869212795",
    "638885417683",
    "442386744353",
    "103105715889",
    "245545462676",
    "472730292857",
    "330188676905",
    "835164637446",
    "792733760839",
    "351501993468",
    "898809789911",
    "895015795356",
    "724002660598",
    "871362719292",
    "807237891255",
    "999911452149",
    "122578899357",
    "710691900526",
    "258307448986",
    "737130764395",
    "907027046896",
    "763603941244",
    "430734990657",
    "503895931360",
    "669540362728",
    "266724342769",
    "514117268639",
    "081325390199",
    "423003514399",
    "249704162688",
    "763008648453",
    "990339680094",
    "211330385671",
    "925152966179",
    "978288397137",
    "105495057255",
    "825641698319",
    "057415533634",
    "520018980103",
    "110948597952",
    "313743910680",
    "272398656194",
    "772153158452",
    "224300973850",
    "353608530281",
    "245179582081",
    "663277389841",
    "107173498710",
    "766337827248",
    "117516905037",
    "712309505854",
    "633353088612",
    "811284229777",
    "151534178276",
    "306415355426",
    "626614931356",
    "156813124566",
    "314815235551",
    "780543022126",
    "544295431143",
    "707077482487",
    "199566480951",
    "263933020539",
    "52832661640",
    "709848358524",
    "844356804704",
    "104374241257",
    "310906938811",
    "394103062818",
    "764974769150",
    "539772159869",
    "601324751636",
    "667973535471",
    "749696950732",
    "756306329178",
    "501404015308",
    "243637512696",
    "753923664805",
    "986000313247",
    "592751261982",
    "683313688378",
    "048819808253",
    "705930551576",
    "257386234256",
    "818342061345",
    "354813040037",
    "737474898029",
    "355873309152",
    "598674086554",
    "503227376785",
    "159807026194",
    "685455198987",
    "782484402741",
    "574779866223",
    "453391408702",
    "742091327244",
    "122526803553",
    "366743142698",
    "422173101802",
    "618459771430",
    "257758044811",
    "746614075791",
    "563282790590",
    "490574956308",
    "249157047649",
    "875698925577",
    "390948362332",
    "785573368785",
    "475088953585",
    "669576153137",
    "732049463269",
    "107072934176",
    "153931337802",
    "254080097072",
    "933208885752",
    "999678624901",
    "126357580389",
    "102471314380",
    "470317259841",
    "451049120500",
    "659782779980",
    "156387875391",
    "174872318107",
    "001633400207",
    "727897471807",
    "174368400705",
    "446299261295",
    "536280801234",
    "692866216735",
    "216881608335",
    "843974653677",
    "293181348795",
    "263625296855",
    "048378556238",
    "204372634319",
    "453000072557",
    "411782140378",
    "007439368137",
    "390780980154",
    "382416733822",
    "746233611703",
    "306986355934",
    "493642496378",
    "276181064229",
    "455444449433",
    "482524230118",
    "833128469047",
    "811711786498",
    "951798379941",
    "143210264188",
    "628508329040",
    "007051062584",
    "894491911112",
    "519511493484",
    "173754725891",
    "813361260812",
    "571004829621",
    "474822919863",
    "914824155844",
    "237065988967",
    "452307495513",
    "217643126080",
    "749857270468",
    "886529160074",
    "680080141114",
    "136845547031",
    "991648021394",
    "314864569078",
    "607024016150",
    "915447279597",
    "184798709955",
    "806072073708",
    "801668240914",
}


def is_1p_image_uri(image_uri: str) -> bool:
    """Shows if the given image_uri is owned by a 1st party account"""
    image_uri_account = image_uri[0:12]
    return image_uri_account in all_accounts
