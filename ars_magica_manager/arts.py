"""The fifteen Hermetic Arts: names, abbreviations, lookups and the
rulebook's description of each."""

TECHNIQUES: tuple[str, ...] = ("Creo", "Intellego", "Muto", "Perdo", "Rego")
FORMS: tuple[str, ...] = (
    "Animal",
    "Aquam",
    "Auram",
    "Corpus",
    "Herbam",
    "Ignem",
    "Imaginem",
    "Mentem",
    "Terram",
    "Vim",
)
ART_ABBREVIATIONS: dict[str, str] = {
    "Creo": "Cr",
    "Intellego": "In",
    "Muto": "Mu",
    "Perdo": "Pe",
    "Rego": "Re",
    "Animal": "An",
    "Aquam": "Aq",
    "Auram": "Au",
    "Corpus": "Co",
    "Herbam": "He",
    "Ignem": "Ig",
    "Imaginem": "Im",
    "Mentem": "Me",
    "Terram": "Te",
    "Vim": "Vi",
}
#: All fifteen Arts, Techniques then Forms.
ARTS: tuple[str, ...] = (*TECHNIQUES, *FORMS)
#: An Art's proper name from its name in any case ("creo" -> "Creo").
ART_BY_NAME: dict[str, str] = {art.lower(): art for art in ARTS}
#: The same, also accepting the two-letter abbreviation ("cr" -> "Creo").
ART_LOOKUP: dict[str, str] = ART_BY_NAME | {
    abbr.lower(): art for art, abbr in ART_ABBREVIATIONS.items()
}
ART_DESCRIPTIONS: dict[str, str] = {
    "Creo": "'I Create' - Creo magic makes things that exist independently into better things of their kind, which includes bringing them into existence from nothing. Things that exist independently are called substances, and include people, trees, and rocks, but do not include colors, weights, and sizes. Creo can thus both create and heal things. Pronounced 'CRAY-oh.'",
    "Intellego": "'I Perceive' - Intellego is the Art of perception. It allows a maga to gather information directly from the forms of things. This information does not deal with the appearances of things, unless Intellego Imaginem magic is used. Rather, it provides information about the actual nature of a thing. Thus, Intellego magic is not deceived by mundane disguises. Pronounced 'in-TEL-le-go.'",
    "Muto": "'I Transform' - By using Muto magic a magus can grant or remove properties something cannot naturally have. Thus, Muto can give a person wings or turn her skin green, or turn a person into a wolf. The difficulty of the magic depends on the extent of the change, so that turning someone's skin green is easy, but turning someone into a golden statue is difficult. Pronounced 'MOO-toe.'",
    "Perdo": "'I Destroy' - Perdo makes things worse examples of the kind of thing they are. It is the opposite of Creo. Perdo magic can simply destroy things, removing them completely from existence, or it can destroy aspects of a thing. Thus, Perdo Corpus could remove a person's weight, while leaving the rest of his properties intact, and Perdo Ignem could make a fire unable to burn anything. Pronounced 'PARE-doe.'",
    "Rego": "'I Control' - The Art of Rego allows a maga to change the state of a thing to some other state that the individual thing can naturally have. Thus, since all things can naturally have any location, Rego magic allows a maga to move things around. Rego can also make a tree blossom out of season, put a person to sleep, shape a piece of stone into a statue, or weave thread into a tunic. Pronounced 'RAY-go.'",
    "Animal": "'animal' - Animal concerns animals of all kinds, from the fish of the sea to the birds of the air. Animal spells cannot affect people, and Hermetic theorists still debate the reason for this. Form Bonus: Soak against animal attacks (claws, bites, etc.), rolls to resist animal poisons. Pronounced 'ah-nee-MAHL.'",
    "Aquam": "'water' - Aquam concerns water and all manner of liquids, as well as properties of liquidity. Form Bonus: Rolls to resist drowning and thirst, soak against water jets and the like. Pronounced 'AH-kwahm.'",
    "Auram": "'air' - Auram is the Art of air, wind, and weather. It also governs gaseous forms in general. Form bonus: Rolls to resist suffocation, including drowning, soak against weather phenomena such as lightning. Pronounced 'OW-rahm.'",
    "Corpus": "'body' - Corpus is the Art of human bodies. This Art affects dead bodies and the bodies of magical or faerie creatures that look human, as well as those of living humans. Since natural philosophy asserts that these things have no more in common than their appearance, and Corpus does not affect human statues, Hermetic theorists are puzzled by the range of this Form. Form bonus: Soak against human unarmed attacks, rolls to resist disease. It does not apply to aging rolls. Pronounced 'COR-poos.'",
    "Herbam": "'plant' - This Form concerns plants and trees. This includes plant matter of all types, including that which is no longer alive — like dead wood and linens. Form bonus: Soak against wooden weapons, rolls to resist herbal poisons, rolls to resist starvation. Pronounced 'HARE-bahm.'",
    "Ignem": "'fire' - This Form concerns fire, heat, and light. Form bonus: Soak against fire and cold. Pronounced 'IG-nem.'",
    "Imaginem": "'image' - This Form concerns the things in the world that the senses respond to. Natural philosophy calls them species (SPEH-kee-ayss, to be distinguished from species of animals and such). All things constantly give off species for each of the senses. Those for touch and taste do not travel far, while those for sight require light to get any distance from the originating body. Imaginem spells normally affect the process by which species are produced, rather than the species themselves. Thus, the species emanating from an illusion are not themselves magical.Form bonus: Rolls to resist confusion, deafening, or nausea caused by sights, sounds, smells, or tastes. Pronounced 'ih-MAH-gih-nem.'",
    "Mentem": "'mind' - This Form concerns minds, thoughts, and spirits. Mentem can also affect the 'bodies' of noncorporeal beings, such as ghosts, as these are maintained in the physical world directly by a spirit's will. Form bonus: Rolls to resist mundane persuasion, deception, or temptation. Pronounced 'MEN-tem.'",
    "Terram": "'earth' - This Form concerns solids, especially earth and stone. Form bonus: Soak against metal or stone weapons, rolls to resist mineral poisons. Pronounced 'TARE-rahm.'",
    "Vim": "'power' - This Form concerns raw magical power. All the Arts rely on the raw energy and potential of magic, but this Art refines the use of magic itself, allowing magi to assume even greater control of their spells. Vim also affects magical, infernal, divine, and faerie creatures. Form bonus: Rolls to resist Twilight, but not rolls to comprehend it; soak total against damage inflicted by your own spell-casting, but not damage inflicted by your own spells. Pronounced 'WEEM.'",
}
