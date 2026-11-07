"""The Theban Tribunal's history, as the book tells it. The book has no
timeline of its own, so the dated events are gathered from its history
of the empire, its chapter on the Order of Hermes and each region's
covenant histories: the founding and end of every covenant, the
Tribunal's meetings and offices, the Sundering of Tremere, and the
empire's wars from Basil II to the eve of 1221, each as a Tribunal Diary
entry. The older mundane history goes, era by era, into the Tribunal's
History.

Dates are AD. Where the book gives a covenant's founding only roughly
("about two centuries ago", "during the 11th century") the entry takes a
round year and says so. Where it gives one event two dates, the Diary
takes the likelier one and the entry mentions the other. Where the book
slips on a ruler's name, the entry uses history's and gives the book's
in brackets. What lies ahead after spring 1220 is not an event yet, so
it closes the History under its Secrets heading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import more_secrets, paragraphs, secrets, titled

if TYPE_CHECKING:
    from . import Theban

#: The title of a record's one secret of table guidance.
NOTES = "Storyguide Notes"

#: The order of the seasons within a year; an entry with none comes first.
SEASON_ORDER = {"": 0, "Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

#: (year, season, title, details, hidden): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str], ...] = (
    # -- Before and beside the Order --
    (
        730,
        "",
        "The League of Iconophiles",
        "Early in the eighth century Greek wizards band together as the League of "
        "Iconophiles, to rescue holy images from the emperors bent on destroying them. "
        "It is the first league worth naming, and its charter is the typikon of "
        "Prokopios, a pre-Hermetic wizard with the Gentle Gift who said the spirit of "
        "Aristotle had dictated it to him. Some thirty years into their struggle the "
        "league's leaders meet Trianoma; they turn down her offer, but the meeting gives "
        "rise to House Jerbiton. (The book gives no exact year.)",
        "",
    ),
    (
        775,
        "",
        "Tremere raids Greece; the Theban League",
        "House Tremere invades Greece, killing wizards and carrying off their vis and "
        "enchanted items. None of the dead belong to the Order, so no Oath is broken. "
        "The Greek wizards unite as the Theban League to drive the raiders back, and "
        "when followers of Jerbiton and Trianoma renew the invitation to join the "
        "Order, many accept, since the Tremere will not attack fellow members. That "
        "protection, more than any battle, ends the raids. Among the League are three "
        "wizards of Hedyosmos, the youngest of whom Guernicus himself teaches Hermetic "
        "magic, and the healers who had restored the old sanctuary of Epidauros. The "
        "enchanters of Hephaistos's forge on Lemnos join in the same years: Ingasia is "
        "younger than Verdi in law, though its members hold it the older forge.",
        "",
    ),
    (
        815,
        "",
        "Dorostolon founded",
        "Tremere magi found Dorostolon, a fortress covenant on the south bank of the "
        "Danube in Bulgaria. Several of the Founder's most powerful lieutenants make "
        "it their base for his plan to rule the Order. In these years Tremere magi "
        "also seize the sanctuary of Epidauros for a time.",
        "",
    ),
    (
        848,
        "",
        "The Sundering of Tremere",
        "Theban magi intercept letters revealing Tremere's design to make himself "
        "master of the Order, and learn that his chief lieutenants will gather at "
        "Dorostolon. A hidden force slips into the covenant and shatters the minds and "
        "loyalties of the lieutenants, and the fortress is torn apart. No one claims "
        "the deed. Local opinion holds that magi of Hedyosmos, with others, loosed "
        "the Titan Typhon from its bonds, struck a pact with it and sent it against "
        "Dorostolon before binding it again. Tremere dies soon afterwards, and the "
        "Tremere usurpers are driven from Epidauros.",
        "Hedyosmos keeps its own records of these years. Tremere magi would dearly "
        "like to read them, and none is welcome there.",
    ),
    (
        855,
        "",
        "Erebos founded",
        "Not long after the Sundering, envoys of the young House Ex Miscellanea reach "
        "Thebes, among them a filius of Pralix sent to deal with the Witches of "
        "Thessaly. A few of the witches, led by the maga Cyra, agree to join the "
        "Order. Unwilling to leave home, Cyra founds a covenant in the Cambunian "
        "mountains and charges it with keeping alive every native Greek tradition "
        "that Tremere had threatened, naming it Erebos, the darkness. (The book places "
        "this only in the second half of the ninth century.)",
        "",
    ),
    (
        865,
        "",
        "The Theban Tribunal instituted",
        "The sixth Grand Tribunal formally creates the Theban Tribunal and names it for "
        "the Theban League. Its lands run from the Ionian Sea to the Black Sea, taking in "
        "the Bulgars' country and Anatolia; Coeris, Tremere's home, is its only domus "
        "magna, a sign of how little the Order then trusts that House. The League's "
        "heirs at once pass Peripheral Code rulings that bring the Tribunal's "
        "government closer to the typikon of Prokopios: the polity, in which the "
        "Hermetic Assembly decides everything and archai drawn by lot only prepare and "
        "carry out its business.",
        "",
    ),
    (
        910,
        "",
        "The automata of the Magnaura",
        "Early in the tenth century the Cretan-born Aella of House Verditius builds "
        "the automata of the Palace of Magnaura in Constantinople. Accused more than "
        "once of serving the emperor as a court wizard, she is never convicted, thanks "
        "largely to the legal skill of her husband, Vaanes of House Guernicus; she is "
        "twice ostracised and twice comes back to tend her creations. (The book gives "
        "no exact year.)",
        "",
    ),
    (
        914,
        "",
        "Estropi founded",
        "A sept of Bjornaer magi, every one with the heartbeast of a bird of prey, "
        "founds Estropi on Mount Erciyes, the highest peak of central Anatolia.",
        "",
    ),
    (
        964,
        "",
        "The Transylvanian Tribunal split off",
        "The rise of the Bulgarian Empire some thirty years after 865, and House "
        "Tremere's slow recovery and growth, persuade the ninth Grand Tribunal that the "
        "Theban Tribunal is too large to govern. Its northern lands become the "
        "Transylvanian Tribunal, and the Theban borders have not moved since.",
        "",
    ),
    (
        980,
        "",
        "Grammaton founded",
        "Grammaton of House Bonisagus and his filii found a covenant, named for him, "
        "to pursue original research into the magic of binding.",
        "",
    ),
    # -- The Bulgar-Slayer and the Schism War --
    (
        1004,
        "",
        "Diadelphia founded",
        "The brothers Cosmas and Baztas of House Verditius found Diadelphia on the "
        "island of Kalymnos. Other Verditius magi join them, but the brothers' bitter "
        "rivalry drives the newcomers away again.",
        "",
    ),
    (
        1014,
        "",
        "Basil II invades Bulgaria",
        "As the Schism War dies away in the west (the Tribunal took almost no part, "
        "though a few Greek magi fought in it), a Byzantine army invades Bulgaria. "
        "After his victory at Kleidion, Basil II is said to blind fourteen thousand "
        "prisoners, sparing one eye in every hundred men to lead the rest home, and "
        "Tsar Samuel dies of the shock at the sight. House Tremere insists Theban magi "
        "helped the emperor; nothing is proved, though some Jerbiton with the Gentle "
        "Gift are close to the imperial family.",
        "",
    ),
    (
        1019,
        "",
        "Bulgaria conquered",
        "Basil II completes the conquest of the Bulgarian state, which becomes a part "
        "of the empire, and restores the old northern frontier on the Danube.",
        "",
    ),
    (
        1020,
        "",
        "Aegaea founded",
        "The Merinita maga Orithyia, coming back from Arcadia, says she was led "
        "through the sea by a golden man with a dolphin's tail, whom she takes for "
        "Triton, Poseidon's herald. She makes a pact with him to dwell in the "
        "undersea palace he showed her, which she takes for Poseidon's own, and names "
        "her covenant Aegaea after it, with Triton as patron. The Tribunal doubts her "
        "until Redcaps confirm the place and its splendour. (The book says only "
        "about two centuries ago.)",
        "",
    ),
    (
        1023,
        "",
        "Gigas founded",
        "Gigas is founded in the forests south-west of Sofia as a place for magi and "
        "trusted companions wounded in the Schism War to recover. The Tribunal "
        "suspects its purpose from the start.",
        "",
    ),
    (
        1025,
        "",
        "Death of Basil II",
        "Basil II, the Bulgar-Slayer, dies without an heir after the most victorious "
        "reign in the empire's history. Some say it was God's punishment for his "
        "cruelty, and for marrying his sister Anna, born in the purple, to Vladimir of "
        "Kiev against the law.",
        "",
    ),
    (
        1028,
        "",
        "The last emperor buried at the Holy Apostles",
        "Constantine VIII is laid to rest in the Church of the Holy Apostles in "
        "Constantinople, the last emperor buried there.",
        "",
    ),
    (
        1030,
        "",
        "The orphanage of St. Christopoulos",
        "Emperor Romanos III Argyros, Zoe's first husband, endows a school and "
        "orphanage at the monastery of St. Christopoulos in Constantinople, paid for by "
        "the treasury and run by the monks. The monastery itself dates from 823.",
        "",
    ),
    (
        1031,
        "",
        "The icon of St. Loukia",
        "Romanos III gives the monastery of St. Christopoulos a tiny and exquisite icon "
        "of a little-known saint, St. Loukia.",
        "",
    ),
    (
        1039,
        "",
        "Kyddopetre founded",
        "A group of Flambeau magi founds Kyddopetre at the Cilician Gates, the narrow "
        "pass through the Taurus mountains into southern Anatolia.",
        "",
    ),
    (
        1050,
        "",
        "Polyaigos founded",
        "Stringes witches nest on the Cycladic island of Polyaigos and plague the "
        "isles around it, Delos among them, sheltering a renegade Flambeau. At the "
        "Assembly's call the hoplite Quaesitor Laskaris fights his way ashore, allies "
        "with Varazes, a drakos giant native to the island, and shields him in a duel "
        "while the giant clubs the renegade to death. Having cleansed the island, "
        "Laskaris founds a covenant there and pledges it to the swift defence of the "
        "Tribunal. (The book says only that this happened in the 11th century.)",
        "",
    ),
    (
        1054,
        "",
        "The Great Schism",
        "Rome and Constantinople finally break over the filioque, the Latin claim that "
        "the Spirit proceeds from the Son as well as the Father. Few think it a "
        "disaster at the time, but the breach has widened into deep mistrust.",
        "",
    ),
    (
        1056,
        "",
        "End of the Macedonian dynasty",
        "The Macedonian dynasty, under which Byzantine power reached its height, ends "
        "with the empresses Zoe and Theodora, born in the purple. Zoe, who ruled "
        "through four husbands, collected magical amulets and automata, some of which "
        "may still survive; after her death the mob put her sister on the throne in "
        "place of her last husband.",
        "",
    ),
    (
        1063,
        "",
        "Miphoria fades; the Crown of Thorns comes to Constantinople",
        "Miphoria, the first covenant of House Mercere, on the coast near Smyrna, had "
        "ridden giant magical sea turtles; the Tribunal told its Redcaps to draw less "
        "mundane notice, and without the turtles the covenant withered. By this year "
        "most of its Redcaps have moved to other covenants. In the same year the Crown "
        "of Thorns is brought from the Holy Land to Hagia Sophia.",
        "",
    ),
    (
        1066,
        "",
        "English axemen in the Varangian Guard",
        "After the Norman Conquest of England, Anglo-Saxon exiles take the place of the "
        "Norsemen in the emperor's Varangian Guard.",
        "",
    ),
    (
        1067,
        "",
        "Cosmas ostracised; Diadelphia disbanded",
        "Cosmas of Diadelphia is ostracised, and to everyone's surprise his rival "
        "brother Baztas leaves the Tribunal with him. With no magi left, Diadelphia "
        "is disbanded by default.",
        "",
    ),
    (
        1069,
        "",
        "Gigas closes to all but Tremere; Estropi flees",
        "Gigas adopts a rule of admitting only magi of House Tremere, which deepens the "
        "Tribunal's distrust. In the same year the Bjornaer of Estropi abandon Mount "
        "Erciyes before the advancing Seljuk Turks.",
        "",
    ),
    (
        1071,
        "",
        "Manzikert",
        "At Manzikert the Seljuk horse archers wear down Emperor Romanos IV Diogenes, "
        "and Andronikos Doukas, commanding the reserve, deliberately withdraws and "
        "leaves him to be captured. Alp Arslan frees Romanos on generous terms within "
        "a week, but the Doukas blind him and repudiate the treaty, and the furious "
        "Seljuks overrun the Anatolian plateau, the empire's granary. The Byzantine "
        "magi living there flee and never return. The icon of St. Loukia cries out a "
        "warning before the battle, and in this year Tikh of Jerbiton, teaching at the "
        "orphanage, notices the icon's strange properties: it portrays Loukia of "
        "Berytus, a Montanist executed for blasphemy, and a Magic aura grows round it.",
        "",
    ),
    (
        1074,
        "",
        "Xylinites founded",
        "Needing room for a laboratory, Tikh of Jerbiton clears and partly drains a "
        "great vaulted cistern beneath the orphanage of St. Christopoulos and founds "
        "Xylinites there, with the icon of St. Loukia as its heart. For the next 130 "
        "years its magi teach at the orphanage, find Gifted foundlings, and build "
        "influence in the palace through the eunuchs the school sends there.",
        "",
    ),
    (
        1075,
        "",
        "Alexandria founded",
        "Methodius, the best-loved Redcap of his day, who claims descent from "
        "Alexander and found the king's flying device in Seljuk lands, chooses an old "
        "fortress on Mount Pagus above Smyrna for a second Mercere covenant. He binds "
        "an eidolon lingering among the ghosts of Alexander's army as its patron, "
        "leaves the walls in ruin to avoid notice, and finishes building this year, "
        "naming the covenant Alexandria.",
        "",
    ),
    (
        1076,
        "",
        "Kyddopetre disbanded",
        "With Cilicia lost to the Sultanate of Rum after Manzikert, the Flambeau of "
        "Kyddopetre, though breaking no law by living outside the empire, feel too cut "
        "off from their Greek sodales and disband.",
        "",
    ),
    # -- The Komnenoi --
    (
        1081,
        "",
        "Alexios Komnenos takes the throne; the Normans land",
        "After the rebellions of Michael VII and Nikephoros Botaneiates, the general "
        "Alexios Komnenos seizes the throne in a daring coup. The same year Robert "
        "Guiscard of Sicily (the book calls him king) takes Durazzo with Norman "
        "knights and Saracen horse, beats the Byzantine army and marches into Greece; "
        "when he is called home, his son Bohemond overruns Macedonia and much of "
        "Thessaly.",
        "",
    ),
    (
        1082,
        "",
        "Venice at Rodos",
        "The Republic of Venice sets up the naval base on Rodos that it still keeps.",
        "",
    ),
    (
        1083,
        "",
        "Anna Komnene born",
        "Anna, the eldest of the nine children of Alexios Komnenos, is born in the "
        "purple. In old age she will write the Alexiad, her life of her father.",
        "",
    ),
    (
        1084,
        "Autumn",
        "Plague ends the Norman war",
        "A terrible plague breaks out in Bohemond's camp and ends the Norman invasion.",
        "",
    ),
    (
        1091,
        "",
        "The Pechenegs crushed at Levounion",
        "A great host of Pecheneg nomads invades. Allied with the Cumans, the "
        "Byzantines all but wipe them out at Levounion; the survivors sue for peace, "
        "and Pecheneg and Cuman horsemen have served in imperial armies ever since.",
        "",
    ),
    (
        1092,
        "",
        "Grammaton disbanded",
        "After more than a century, and some notable discoveries, it is plain that "
        "Grammaton's research into binding magic will never reach its goal. The "
        "covenant disbands and its magi join others.",
        "",
    ),
    (
        1095,
        "",
        "A Latin patriarch of Antioch",
        "When crusaders take Antioch a Latin patriarch is set up there, driving the "
        "Orthodox patriarch into exile; his successor Dorotheus now lives at Nicaea. "
        "(The book dates this 1095; Antioch actually fell in 1098.)",
        "",
    ),
    (
        1096,
        "",
        "The First Crusade",
        "Answering the emperor's plea for help, Pope Urban preaches a crusade. Alexios "
        "wanted mercenaries, not armies that might keep his lost lands, and has the "
        "crusaders shadowed by Pecheneg and Cuman horse as they plunder their way "
        "across the empire. He refuses to ship them to Asia until their lords swear to "
        "return former imperial lands; only Raymond of Toulouse keeps his word, and "
        "each side comes away feeling betrayed. (The book dates the crusade "
        "1091 to 1108.)",
        "",
    ),
    (
        1098,
        "",
        "A second Holy Lance",
        "During the First Crusade a second, longer lance is found, which also seems to "
        "be a true relic.",
        "",
    ),
    (
        1100,
        "",
        "Ephesus recovered",
        "After nearly forty years of Seljuk rule, Ephesus returns to the empire and is "
        "renamed Hagios Theologos, but it dwindles to a few hundred souls by a silted "
        "harbour.",
        "",
    ),
    (
        1101,
        "",
        "The Court of Fools founded",
        "Mystics and soothsayers of House Ex Miscellanea form the Court of Fools, a "
        "wandering covenant that travels the Greek mainland.",
        "",
    ),
    (
        1109,
        "",
        "Wilusa founded and lost",
        "After many such proposals, the Tribunal finally lets Droserius of House "
        "Merinita and four companions found Wilusa at Ilion, where he says the spirit "
        "of the river Scamander, dwelling in a regio, has promised to be their patron. "
        "By the next Tribunal the covenant and all its magi have vanished, and no "
        "search finds any trace. The Tribunal has refused every later plan for a "
        "covenant there.",
        "Droserius and his companions are trapped in one of Ilion's Faerie regiones, "
        "made to fight the fall of Troy over and over.",
    ),
    (
        1110,
        "",
        "Petronas becomes logothete",
        "Petronas of House Mercere begins nearly a hundred years as the Tribunal's "
        "logothete. (The book says only that he served for almost a century before "
        "1207.)",
        "",
    ),
    (
        1111,
        "",
        "Genoa and Pisa win trading rights",
        "With Alexios fighting the Turks in Asia, the fleets of Genoa and Pisa gather "
        "off the Ionian coast and force trading privileges like those Venice already "
        "holds. Native Greek trade and the imperial fleet decline from this time.",
        "",
    ),
    (
        1115,
        "",
        "Thermakopolis founded",
        "Jerbiton magi found Thermakopolis in Constantinople, sworn to preserve and "
        "protect the city: the pride, and later the shame, of their House.",
        "",
    ),
    (
        1118,
        "",
        "Ioannes II Komnenos",
        "Ioannes II, a pious and swarthy man called both the Beautiful and the Moor, "
        "succeeds his father despite palace plots. When he revokes the Venetians' "
        "privileges, their fleet seizes several great islands, and he has to restore "
        "them to win the islands back.",
        "",
    ),
    (
        1123,
        "",
        "Lamites founded",
        "Magi devoted to prophecy found Lamites in Anatolia and claim the Phrygian "
        "Sibyl as their patron.",
        "",
    ),
    (
        1127,
        "",
        "Lamites destroyed",
        "Everyone at Lamites dies, most believe at the hands of Lamia, angered by their "
        "presumption; it may instead have been the faerie Lamia, resenting rivals.",
        "",
    ),
    (
        1143,
        "",
        "Manuel I Komnenos",
        "Manuel I, tall, athletic, a great huntsman, warrior and notorious seducer, "
        "takes the throne.",
        "",
    ),
    (
        1147,
        "",
        "The Second Crusade; Roger II takes Thebes",
        "The Second Crusade passes through the empire with more looting and ends in "
        "disaster, and relations with the crusaders sink further. About this time "
        "Roger II of Sicily ravages the Morea, takes Thebes and Athens, and carries "
        "the Theban silk industry, workers and all, off to Sicily; Thebes later "
        "recovers. (The book dates the crusade 1143 to 1149 and puts Roger's raid in "
        "the middle of the century.)",
        "",
    ),
    (
        1151,
        "",
        "Thumachia founded",
        "Mostly Jerbiton magi found Thumachia to guard the Tribunal's western border "
        "after the ravages of the Second Crusade, treading carefully between meddling "
        "in mundane affairs and protecting their sodales.",
        "",
    ),
    (
        1157,
        "",
        "Euboea sacked",
        "William I of Sicily, called the Bad, lands ten thousand men from 164 ships "
        "and sacks every coastal town of Euboea, which never recovers its old "
        "prosperity.",
        "",
    ),
    (
        1163,
        "",
        "Moero's Garden founded",
        "Ionnia of House Jerbiton, a minor noble who loves the women poets, finds the "
        "house of the poet Moero in one of Constantinople's empty quarters, summons "
        "her ghost as patron and invites aristocratic Jerbiton sodales to join her. "
        "The covenant is pledged to recovering early Byzantine art and letters, and "
        "its members must live, like senators, from land others work.",
        "",
    ),
    (
        1170,
        "",
        "Memnos plans Favonius",
        "On his travels through mainland Greece, Memnos of Verditius meets Dryops, the "
        "spirit of an oak forest, who is bored and longs to see the world. Memnos has "
        "the forest felled and carried to his workshop on Andros, the spirit with it, "
        "and spends decades planning a ship of its wood that the spirit will inhabit "
        "and fill with a Magic regio. Having grown terrified of the sea, he gives the "
        "finished Philomela to his apprentice to captain; when the Procne joins her, "
        "the covenant takes the name Favonius. In these years too Ausculator takes his "
        "mater's place at the head of Hedyosmos. (The book says some fifty years "
        "ago.)",
        "",
    ),
    (
        1171,
        "",
        "War with Venice",
        "When the Genoese colony at Galata is burned, Manuel blames Venice and "
        "imprisons ten thousand Venetians in Constantinople. The Venetian fleet sails "
        "against the empire, but plague strikes it at Chios and it limps home carrying "
        "death to Venice; peace follows and the prisoners go free.",
        "",
    ),
    (
        1180,
        "",
        "Renier of Montferrat marries Maria Komnene",
        "Boniface of Montferrat's brother Renier marries Maria Komnene, giving the "
        "family the claim to Thessaloniki that Boniface will later press. Manuel I "
        "dies this year, leaving an infant heir; about now Andronikos Komnenos builds "
        "the palace of Nymphaion south of Smyrna.",
        "",
    ),
    (
        1182,
        "",
        "Andronikos enters Constantinople; the Latins massacred",
        "Andronikos Komnenos rides into Constantinople at the head of an army and has "
        "his rivals murdered, Renier of Montferrat among them. The mob turns on the "
        "Venetians and then on every Westerner, killing tens of thousands, even the "
        "sick in their beds. Venice and Montferrat do not forget.",
        "Andronikos, exiled for plotting against Manuel, had sold his soul to a demon "
        "in a woman's shape for the throne.",
    ),
    (
        1183,
        "",
        "Andronikos the Tyrant crowned",
        "Andronikos I becomes emperor and rules by torture and executions.",
        "",
    ),
    (
        1185,
        "Summer",
        "The sack of Thessaloniki",
        "William II of Sicily takes Durazzo without a fight and marches along the Via "
        "Egnatia. In August Thessaloniki falls: its defenders inexplicably run out of "
        "missiles, the walls give way as if by magic, St. Demetrios does not rise to "
        "defend it, and five thousand die amid unheard-of sacrilege, leaving a strong "
        "Infernal aura. Thumachia is sacked in the same war; its survivors join "
        "Thermakopolis. In answer to the outrage two holy magae, the sisters Anna and "
        "Theocharista Psellus, found the convent of Koukoubiou and with it Oikos tou "
        "Eleous, the House of Mercy; the novice Gemma has been with them ever since.",
        "Behind the sack the sisters find a widespread diabolist circle among the "
        "Paulicians of Thessaloniki, which they still fight.",
    ),
    (
        1185,
        "Autumn",
        "Andronikos falls; Isaac II Angelos",
        "Andronikos orders hundreds more executions; the mob rises from Hagia Sophia, "
        "his soldiers refuse to fire on it, and he is caught, blinded in one eye, and "
        "tortured to death in the streets, while the palaces and many relics are "
        "plundered. His ghost still rides on moonless nights. Isaac II Angelos is "
        "raised to the throne, and the rising spreads to Thessaloniki, where the "
        "Sicilians are routed and cut down. The same year House Tremere backs the "
        "lords leading a Bulgarian revolt with advice and materials, though not "
        "troops; in reply a few Greek magi form the League of Advisors and go to "
        "court in Constantinople, offering counsel unpaid and keeping just short of "
        "the forbidden role of court wizard.",
        "",
    ),
    (
        1186,
        "",
        "The logothete made permanent",
        "The Tribunal passes a motion making the logothete, until now elected from the "
        "Redcaps every seven years, a permanent post, to spare the bureaucracy a "
        "changing administration. A new logothete is chosen only on death, Twilight, "
        "resignation or a failed vote of confidence among the Redcaps.",
        "",
    ),
    (
        1190,
        "",
        "Barbarossa's crusade; the battle standard lost",
        "Frederick Barbarossa's crusade marches overland through the empire; Isaac's "
        "own envoys urge him to take Constantinople, he occupies Philippopolis and "
        "Didymoteichon, and Isaac must ferry his army across the Bosporus. Isaac then "
        "leads the army of Constantinople against the rebel Bulgarians and is routed; "
        "the imperial battle standard, a holy relic of the emperors, is last seen in "
        "that army.",
        "",
    ),
    (
        1191,
        "",
        "Richard takes Rodos",
        "During the Third Crusade Richard the Lionheart takes Rodos and recruits its "
        "sailors.",
        "",
    ),
    (
        1195,
        "Spring",
        "Alexios III Angelos",
        "In April Isaac II is overthrown and blinded by his brother, who becomes "
        "Alexios III and pays for tribute to the German emperor Henry VI with the "
        "hated Alamanikon tax. Central authority crumbles; Leo Sgouros makes himself "
        "master of the Morea, and local rulers spring up across the mainland.",
        "",
    ),
    # -- The Fourth Crusade --
    (
        1202,
        "",
        "The crusaders sack Zara",
        "The Fourth Crusade, meant for Egypt, cannot pay Venice for the fleet it "
        "ordered after far fewer knights arrive than planned. To reduce the debt the "
        "crusaders take and plunder Zara, a Christian city, for Venice, and the pope "
        "excommunicates them. At Zara Prince Alexios, son of the deposed Isaac, offers "
        "money and troops if they will restore his father.",
        "Infernal agents worked in every army of the crusade. Their excommunication "
        "left the knights without Divine protection, and several nobles made pacts "
        "with demons; the whole design was the work of Akgah, a prince of Hell.",
    ),
    (
        1203,
        "Summer",
        "The first siege of Constantinople",
        "Porphyrio, the giant whale that Belisarius once fought, surfaces in April, "
        "a week before the Venetian fleet fills the Sea of Marmara. In June the "
        "crusaders storm the tower at Galata and break the great chain across the "
        "Golden Horn. After a month's siege Alexios III flees by night, and the prince "
        "is crowned Alexios IV beside his blind father, Isaac II.",
        "",
    ),
    (
        1203,
        "Autumn",
        "The Great Fire",
        "In August crusaders attack a mosque outside the walls; driven back by the "
        "locals, they set houses alight, and the wind carries the fire into the city. "
        "It burns for three days and leaves 440 acres in ashes, which are still a "
        "waste in 1220. The emperors, unable to pay what they promised, lose the "
        "people's goodwill.",
        "",
    ),
    (
        1204,
        "Winter",
        "Murzuphlos seizes the throne",
        "In January the mob gathers at Hagia Sophia and Alexios Doukas, called "
        "Murzuphlos, takes power in a palace coup; Isaac and Alexios IV die (some say "
        "Isaac of age and shock). Crowned Alexios V, he strengthens the walls and "
        "rejects the crusaders' claims. In a skirmish at Philia he loses his crown "
        "and the Hagka banner to raiding French knights.",
        "",
    ),
    (
        1204,
        "Spring",
        "The fall of Constantinople",
        "In April the second assault carries the walls: the cleric Aleaumes of Clari "
        "hurls himself through a breach, the defenders panic, and Murzuphlos slips "
        "away by night. Constantine Laskaris is acclaimed in Hagia Sophia but flees at "
        "dawn as the army deserts, and the city suffers three days of murder, rape and "
        "sacrilege. The magi of Thermakopolis, trusting their Mentem magic to keep the "
        "peace, fail, and their spells frighten their own side off the walls; four of "
        "them die, and Michael dies last, after binding his apprentice Petros, Wilrich "
        "of Flambeau and three Jerbiton survivors to defend the city for ever. Only "
        "Mathieus escapes, to Normandy. The Court of Fools, visiting the city, burns "
        "with it. Three Jerbiton of Xylinites fall fighting, the rest flee into exile "
        "and Artoud of Criamon stays on alone (the book dates this once to 1205). "
        "Moero's Garden flees with the Greek nobles to its chapter house in Nicaea, "
        "leaving most of its treasures behind. The icon of St. Loukia screams a "
        "warning for the third time this spring.",
        "In the Hippodrome the demon Akgah, a vast two-headed winged leopard, fights "
        "the Hagka and wins; crusaders who see it think it the lion of Venice. In "
        "these days someone also took the palladium and its relics from under the "
        "Column of Constantine, and the city's ancient Divine wards fell. The "
        "survivors who swore Michael's oath hid in the catacombs, helped by a "
        "humanoid figure of living rock.",
    ),
    (
        1204,
        "Summer",
        "The Latin Empire",
        "By the partition agreed in March, the emperor takes a quarter of the empire "
        "and Venice and the crusader lords three-eighths each. Electors choose "
        "Baldwin of Flanders as Emperor Baldwin I over Boniface of Montferrat. Venice "
        "claims Candia, Rodos, Karpathos, the Cyclades, Durazzo and, of the northern "
        "isles, only Lemnos, Ingasia's island, which takes the Lemnian Earth and "
        "leaves the covenant poorer; some magi suspect Verditius of a deal with the "
        "doge. Boniface marches on Thessaloniki, where the Greeks welcome him, and "
        "only Doge Dandolo's diplomacy stops a war with Baldwin. Greek leaders flee to "
        "Arta and to Nicaea, where Theodore Laskaris sets up a court in exile; "
        "Alexios and David Komnenos seize Trebizond.",
        "",
    ),
    (
        1204,
        "Autumn",
        "The League of Advisors disbanded",
        "Accusations fly: House Tremere is blamed, and so is House Jerbiton. The "
        "League of Advisors, which lost many members with Thermakopolis, cannot "
        "survive the charge of meddling with mundanes and breaks up. The Tribunal "
        "fails to convict its surviving members.",
        "",
    ),
    (
        1205,
        "Spring",
        "Adrianople",
        "The attempt to impose feudal rule on Thrace sets off a Greek revolt backed by "
        "Tsar Kaloyan of Bulgaria. On 14 April the Bulgarians ambush the Latins at "
        "Adrianople; Louis of Blois is killed by Cumans and Baldwin is captured and "
        "never seen again. Doge Enrico Dandolo dies the same year, and the captured "
        "Murzuphlos is thrown to his death from the Column of Theodosius.",
        "A Redcap who whispered that House Tremere knew more of Baldwin's fate died "
        "soon after in a fall from his horse, and the archai of the day let the "
        "matter drop. One tale says his skull became a drinking cup.",
    ),
    (
        1205,
        "Summer",
        "Henry I crowned; Achaea and Athens founded",
        "When news of Baldwin's death arrives, his brother is crowned Emperor Henry I "
        "on 20 August, ruling a narrow strip round Constantinople. In the Morea "
        "William de Champlitte and Geoffrey de Villehardouin beat an army ten times "
        "their number from Epiros at the Olive Grove of Koundouros and found the "
        "Principality of Achaea; the defeated Michael Komnenos Doukas retreats to Arta "
        "and founds Epiros. (The book also dates Achaea's founding to 1204.) Otto de "
        "la Roche founds the Duchy of Athens, and the monastery of Daphni is sacked "
        "and given to the Cistercians. At Nicaea Theodore Laskaris names Michael "
        "Autoreianos Orthodox patriarch, and the Venetians begin walling their "
        "quarter of Constantinople.",
        "",
    ),
    (
        1207,
        "Summer",
        "The Tribunal of 1207",
        "The first Tribunal since the fall meets on Delos. Michael's Tabula is "
        "formally founded by the survivors who swore Michael's oath, named for the "
        "stone tablet on which it was carved. Petronas abdicates as logothete after "
        "almost a century and Leontius of Alexandria, an unhappy choice, replaces "
        "him. Maria Laskarina of Polyaigos, filia of its founder, is elected "
        "polemarch. Krum of Bjornaer, late of Moero's Garden, hears Lucian of Aegaea's "
        "tales of Poseidon and joins Aegaea. Frankish magi found Novocastrum on the "
        "western borders of the Kingdom of Thessaloniki. (The book gives no season "
        "for the meeting.)",
        "",
    ),
    (
        1207,
        "Autumn",
        "St. Demetrios slays Kaloyan; Boniface killed",
        "Boniface of Montferrat dies in a Bulgarian ambush and his head is sent to "
        "the tsar, leaving his two-year-old son Demetrios heir to Thessaloniki under "
        "Queen Margaret, who soon marries Nicholas of St. Omer, a lord of Thebes. "
        "Kaloyan (the book also calls him Ioannitsa) besieges the city; the sisters "
        "of Oikos tou Eleous call on St. Demetrios, and early in October a shining "
        "armoured rider comes out and kills the tsar with a spear. The Bulgarians say "
        "his Cuman commander did it. Henry's battles reopen the road between the two "
        "Latin states, and his wife Agnes of Montferrat dies. Marco Sanudo attacks "
        "Naxos. Seirene twins from Lesbos join Oikos tou Eleous and secretly back "
        "Queen Margaret.",
        "",
    ),
    (
        1208,
        "",
        "Theodore Laskaris crowned; Leo Sgouros leaps",
        "Theodore I Laskaris (the book calls him Theodore II) is crowned emperor at "
        "Nicaea, vowing to retake Constantinople. Trapped in Acrocorinth, Leo Sgouros "
        "rides his horse off the battlements to his death, and Greek resistance in the "
        "Morea falters. Otto de la Roche takes the title of duke.",
        "",
    ),
    (
        1209,
        "",
        "Demetrios crowned; Oberto seized",
        "Demetrios is crowned king of Thessaloniki at four. Count Oberto of Biandrate, "
        "who has forced Margaret from the regency to put William VI of Montferrat on "
        "the throne, shuts the gates against Henry, but Henry, once admitted, takes "
        "Margaret's side and has Oberto chained in the castle of Serres. In the Morea "
        "William de Champlitte dies on his way to France, and Geoffrey de "
        "Villehardouin, regent, contrives with Venice to delay the heir and keeps the "
        "principality.",
        "",
    ),
    (
        1210,
        "",
        "Epiros turns on Thessaloniki",
        "Michael Komnenos Doukas, allied with Venice, attacks Thessaloniki and his "
        "son-in-law the boy king; Henry intervenes to save Demetrios from Venice, the "
        "Bulgarians and Epiros. Michael's half-brother Theodore Komnenos Doukas "
        "defects from Nicaea to Epiros. Porphyrion of Tytalus leaves Hedyosmos for "
        "Rome.",
        "In Rome Porphyrion is rumoured to have found the Jar of Pandora before moving "
        "on to Normandy, where he may bid to become primus of Tytalus.",
    ),
    (
        1211,
        "",
        "Antioch-on-the-Maeander",
        "Theodore Laskaris marches out of Philadelphia and defeats Sultan Kaykhusraw I "
        "of Rum; the Maeander becomes Nicaea's southern border. Greek chroniclers say "
        "the sultan had struck the emperor down when a mysterious French knight "
        "appeared from nowhere and killed him, and the Tribunal whispers that the "
        "knight was a magus. The Latin patriarch Thomas Morosini dies, and the whole "
        "Morea is now in Latin hands.",
        "",
    ),
    (
        1212,
        "",
        "Novocastrum destroyed; Candia and Naxos",
        "Epiros overruns the western borders of Thessaloniki, and the Frankish magi of "
        "Novocastrum die resisting it; few mourn them. Venice ousts the Genoese pirate "
        "Enrico Pescatore and establishes the Kingdom of Candia. Marco Sanudo has "
        "taken nearly all the Cyclades and parcels them into some fifty lordships of "
        "the Duchy of Naxos. Nicaea takes back most of David Komnenos's conquests.",
        "",
    ),
    (
        1213,
        "",
        "Epiros turns on Venice",
        "Michael of Epiros starts taking the towns of the Adriatic and Ionian shores "
        "from Venice, his ally of three years before.",
        "",
    ),
    (
        1214,
        "Summer",
        "The Tribunal of 1214",
        "The Tribunal meets on Delos. Aiakia of Hedyosmos is elected archon and Maria "
        "Laskarina re-elected polemarch. Leontius, the logothete, narrowly escapes "
        "ostracism over his faulty register of tokens and shards. (The book gives no "
        "season for the meeting.)",
        "",
    ),
    (
        1214,
        "",
        "Corfu and Amastris taken; peace with the Latins",
        "Michael of Epiros wrests Corfu from Venice. Theodore Laskaris takes Amastris "
        "on the Black Sea, still his eastern border; the Sultanate of Rum drives "
        "north between Nicaea and Trebizond and kills David Komnenos. Nicaea makes "
        "peace with the Latin Empire, which holds for six years.",
        "",
    ),
    (
        1215,
        "",
        "Michael of Epiros murdered",
        "Michael Komnenos Doukas is stabbed by a servant driven past bearing by his "
        "cruelty, and his half-brother Theodore succeeds him, taking Ohrid and "
        "Pelagonia from the Bulgarians. Gervase becomes Latin patriarch of "
        "Constantinople after four years' vacancy.",
        "",
    ),
    (
        1216,
        "",
        "Death of Emperor Henry",
        "Henry marries Maria of Bulgaria, Kaloyan's daughter, and dies suddenly the "
        "same year, poisoned, people say, by her or by Count Oberto; Maria vanishes. "
        "The barons elect Peter of Courtenay, Henry's brother-in-law, who accepts "
        "William of Montferrat's claim to Thessaloniki, and Margaret flees into exile, "
        "leaving her son in the city. Ravano dalle Carceri, lord of Negroponte, dies, "
        "and Venetian bailiffs split his three baronies into six. A peace treaty "
        "settles the Troad.",
        "Hermetic gossip ties the vanished Maria of Bulgaria to the Daughters of "
        "Erichtho.",
    ),
    (
        1217,
        "",
        "Peter of Courtenay captured; Yolanda regent",
        "Peter is crowned by the pope and lands at Durazzo with 5,500 men, but "
        "Theodore of Epiros seizes him on the Via Egnatia; he dies a prisoner, "
        "almost certainly murdered, though no grave is known. His wife Yolanda of "
        "Flanders reaches Constantinople by sea and rules as regent, making peace with "
        "Bulgaria and Nicaea.",
        "",
    ),
    (
        1218,
        "",
        "Geoffrey II of Achaea; Ivan Asen II",
        "Geoffrey de Villehardouin dies and his son Geoffrey II, husband of Yolanda's "
        "daughter Agnes, succeeds him; generous to Greeks and Latins, he taxes Latin "
        "church lands and spares the Orthodox clergy. In Bulgaria Ivan Asen II takes "
        "the throne from Tsar Boril (the book still names Boril as tsar).",
        "",
    ),
    (
        1219,
        "",
        "Death of Yolanda",
        "Yolanda marries her daughter Marie of Courtenay to Theodore Laskaris and dies "
        "suddenly. Her elder son Philip of Namur refuses the throne; his brother "
        "Robert of Courtenay accepts it but has not yet arrived, and the Latin Empire "
        "is leaderless. The Latin patriarch Gervase dies too, and the Serbian Church "
        "becomes autocephalous. In August Venice and Nicaea agree a trade treaty, "
        "ending the Nicene navy's war on Venetian shipping.",
        "",
    ),
    (
        1220,
        "Spring",
        "Nicaea at war again",
        "The peace with the Latins breaks and Theodore Laskaris masses his army to "
        "take Holkos on the Hellespont while the Latin knights are away fighting the "
        "Bulgarians. He also gathers churchmen at Nicaea to seek an end to the schism "
        "with Rome. Several magi of the Court of Fools, lost in 1204, reappear.",
        "",
    ),
)

#: The older history of the lands, era by era, for the Tribunal's History.
ERAS: tuple[tuple[str, str], ...] = (
    (
        "Heroes and city-states",
        "The Greeks tell of five races of men, from the golden race under Kronos to "
        "the present race of iron, and St. Jerome's Chronicon sets the heroes' deeds "
        "beside the Bible's: Perseus and Medusa, the Argonauts, Theseus and the "
        "Trojan War. The historians who followed, Herodotus, Thucydides, Xenophon and "
        "Polybios, wrote the gods out of their accounts. Persia's invasions were "
        "beaten at Marathon, Salamis and Plataea, though its kings brought sorcerers, "
        "jinn and fly-spirits to war, and the Greek theurgists turned to the Witches "
        "of Thessaly to bind them. The Delian League met on Delos; Athens and Sparta "
        "then fought the Peloponnesian War from 431 to 404 BC.",
    ),
    (
        "Macedon and Rome",
        "Philip II of Macedon mastered Greece, and Alexander conquered Persia, the "
        "romances say with sorcery learned from his true father Nectanabus, and cursed "
        "his sister into the half-fish Gorgona. His successors split the world into "
        "warring kingdoms, and the leagues of Greek cities rose and fell until Rome "
        "took Macedonia in 168 BC and the rest of Greece in 146 BC. Paul preached at "
        "Athens and Corinth, Diocletian divided the empire, and Constantine, after "
        "his vision at the Milvian Bridge, called the Council of Nicaea in 325 and in "
        "330 founded Constantinople, ploughing its bounds to bind its spirits under "
        "a great Divine ward.",
    ),
    (
        "Justinian and the Arabs",
        "The Goths beat the eastern army at Adrianople in 378 and lorded it in the "
        "capital until a riot drove them out in 400. Justinian codified Roman law, "
        "built Hagia Sophia and crushed the Nika riot of 532, at a cost of thirty "
        "thousand dead in the Hippodrome; demons may have steered its Blue and Green "
        "factions for centuries. Phocas's tyranny let the Slavs settle across Greece "
        "until Heraclius beheaded him in 610 and beat Persia at Nineveh. The Arabs "
        "took North Africa by 711 and besieged the capital in 674 to 678 and 717 to "
        "718, and the empire was reordered into military themes.",
    ),
    (
        "Icons and Bulgars",
        "The emperors' war on icons lasted a century, until the Regent Theodora "
        "restored them for good in 843; Empress Irene had already been exiled to "
        "Lesbos in 802. The Bulgars founded a state in the Balkans in 680 and, "
        "despite their conversion by Cyril and Methodius in 864, fought the empire "
        "for the Balkans, often with House Tremere's favour. From 800 the empire "
        "pushed the Slavs out of Greece, and under the Macedonian dynasty, from 867, "
        "it retook Crete, Cyprus, Antioch and Tarsus, though Sicily was lost in 902. "
        "The Image of Edessa came to Hagia Sophia in 944, the Great Lavra opened on "
        "Mount Athos in 955, Emperor Ioannes I broke the Rus with a thirteenth charge "
        "in 971, Basil II began his reign in 976, and the Paulicians won freedom of "
        "worship in 990.",
    ),
)

#: What lies ahead after spring 1220, for a saga that follows the book.
FUTURE = [
    titled(
        "The Tribunal of 1221",
        "The Theban Tribunal next meets on Delos in 1221. Leontius means to "
        "resign as logothete there, and the Redcaps plan to propose Proximios.",
    ),
    titled(
        "Pancratius's Gauntlet",
        "Pancratius, Syagricus's apprentice, hopes for his Gauntlet at the "
        "Tribunal of 1221.",
    ),
    titled(
        "The Ceremony of Propitiation",
        "At the Tribunal of 1221 the League Against Idolatry presses to end "
        "the Ceremony of Propitiation.",
    ),
    titled(
        "The League of Advisors tried again",
        "House Tremere has asked the Grand Tribunal of 1228 to try the two "
        "surviving members of the League of Advisors again.",
    ),
    titled(
        "The Verditius Contest of 1234",
        "The Verditius Contest of 1234 will test whether Ingasia is now the "
        "House Verditius's domus magna.",
    ),
    titled(
        "What Proximios means to do",
        "Proximios of Alexandria, founder of the League of the Vigilant, is "
        "an Infernalist who means to bring the Order down, starting in Thebes.",
    ),
    titled(
        "Storyguide Notes",
        "If the saga follows history, Robert of Courtenay reaches "
        "Constantinople in 1221, Theodore Laskaris takes Holkos, and the "
        "Latins, beset from the north, sue for peace that year.",
    ),
]


def build(theban: Theban) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, in order of
    year and season, and add the older history, by era, to the Tribunal's
    History, with what lies ahead under Secrets. Nothing is written when
    the Tribunal has not been made yet (the parts build in order, this
    one after the Tribunal's)."""
    tribunal = theban.tribunal
    if tribunal is None:
        return
    for year, season, title, details, hidden in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        theban.b.event(tribunal, year, title, secrets(details, hidden), season=season)
    eras = paragraphs(*(f"{title}. {text}" for title, text in ERAS))
    # Any history already written keeps its place, its secrets ahead of ours.
    tribunal.history = paragraphs(tribunal.history, eras)
    tribunal.secrets = more_secrets(tribunal.secrets, FUTURE)


def finish(theban: Theban) -> None:
    """Join the Storyguide Notes the parts gave the Tribunal into one,
    last, once every part's secrets are in (this part finishes after
    the stories')."""
    if theban.tribunal is not None:
        theban.tribunal.secrets = more_secrets(theban.tribunal.secrets)
