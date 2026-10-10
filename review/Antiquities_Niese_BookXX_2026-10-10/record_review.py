"""Record explicitly read sections and manually chosen Latin phrases."""
from prepare import *
from mixed_mapper import Book
def record(name,choices):
    model=Book(PACK/'frozen-inputs/Latin.xml');rows=json.loads((PACK/'IDENTITIES.json').read_text(encoding='utf-8'));records=[]
    for choice in choices:
        n,phrase,pdf,comment=choice[:4];print_context=choice[4] if len(choice)>4 else None
        row=rows[n-1];assert row['Latin_review_status']=='PENDING',n
        if phrase is None:
            item=dict(number=n,Latin_start=None,Latin_locator=None,assessment='EDITORIAL_DECISION_REQUIRED',correspondence='NO_INDEPENDENT_LATIN_INTERVAL_CANDIDATE',review_note=comment,source_sha256=sha(model.raw),Greek_print=dict(volume='IV',year=1890,printed_page=pdf-14,PDF_image_page=pdf,evidence=info(PACK/f'evidence/Niese-IV-PDF{pdf:03}.jpg'),marginal_identity=n,labelled_line_context=print_context or 'XML incipit corroborated in printed context: '+row['Greek_text'].strip()[:130],precision='Marginal line label, not a word tag.',action='RETAIN_EXISTING_XML_NUM'),review_method='Entire Greek section read; normal Latin slot read; whole-book displacement audit still required before asking for editorial decision.')
            row.update(candidate=item,print_review_status='VISUALLY_REVIEWED',Latin_review_status='EDITORIAL_DECISION_REQUIRED');records.append(item);continue
        hits=[m.start() for m in re.finditer(re.escape(phrase),model.stream)]
        assert len(hits)==1,(n,phrase,hits)
        k=hits[0];loc=model.locate(k);unit=model.units[loc['paragraph']-1]
        status='EXACT_START' if k==unit['book_start'] else 'INTERNAL_BUT_EXACT'
        item=dict(number=n,Latin_start=k,Latin_locator=loc,Latin_phrase=phrase,assessment=status,correspondence='PRESENT',review_note=comment,Greek_print=dict(volume='IV',year=1890,printed_page=pdf-14,PDF_image_page=pdf,evidence=info(PACK/f'evidence/Niese-IV-PDF{pdf:03}.jpg'),marginal_identity=n if n>1 else 'implicit first Niese identity at traditional I.1',labelled_line_context=print_context or 'XML incipit corroborated in printed context: '+row['Greek_text'].strip()[:130],precision='Marginal numeral labels a printed line; it does not tag an XML word.',action='ADD_IMPLICIT_OPENING_AFTER_DURATION_NOTICE' if n==1 else 'RETAIN_EXISTING_XML_NUM',XML_start=row['Greek_text'].strip()[:180],XML_end=row['Greek_text'].strip()[-180:]),source_sha256=sha(model.raw),review_method='Complete Greek section and neighboring context read; complete actual aligned Latin unit read; phrase chosen by individual semantic and syntactic comparison, not numeric suffix.')
        row.update(candidate=item,print_review_status='VISUALLY_REVIEWED',Latin_review_status='INDIVIDUALLY_REVIEWED');records.append(item)
    save(PACK/f'review-{name}.json',records);save(PACK/'IDENTITIES.json',rows)
    print('Recorded',len(records),'individual reviews; cumulative',sum(r['Latin_review_status']=='INDIVIDUALLY_REVIEWED' for r in rows))
if __name__=='__main__':
    record('001-022',[
        (1,'Moriente siquidem agrippa',290,'Death of Agrippa and replacement of Marsus; duration notice belongs outside narrative.','I.1 Τελευτήσαντος δὲ τοῦ βασιλέως Ἀγρίππα'),
        (2,'Fatus itaque dum',290,'Fadus arrival, Peraean dispute and unauthorized attack remain together.','Φᾶδος δὲ ὡς εἰς τὴν Ἰουδαίαν'),
        (3,'Haec audiens fatus',290,'Anger at bypassing his judgment; next relative clause begins arrest.','σουσιν. ταῦτα πυθόμενον τὸν Φᾶδον'),
        (4,'qui sumens tres',290,'Latin relative clause supplies the arrest; preserve its attachment and preceding comma.','ἀλλ᾽ ἐφ᾽ ὅπλα χωρήσειαν. λαβὼν οὖν τρεῖς'),
        (5,'II Tholomeus autem',291,'Tholomeus arrest and clearing of brigands; literal II stays unchanged.','φυγὴν ἐπέβαλεν. ἀναιρεῖται δὲ καὶ'),
        (6,'III Is enim fadus',291,'High-priestly garment order; literal III retained at its own chapter point.','τῇ Φάδου· ὃς δὴ καὶ τότε μεταπεμψάμενος'),
        (7,'Illi uero nequaquam',291,'Refusal to contradict and request for embassy and waiting for reply.','καθὰ δὴ καὶ πρότερον ἦν. οἱ δὲ'),
        (8,'Illi uero ita se',291,'Conditional permission and handing over child hostages.','οἱ δὲ ἐπιτρέψειν αὐτοῖς ἔφασαν'),
        (9,'Cumque romam uenissent',291,'Arrival in Rome and Agrippa petition; continuation on following page preserved.','ἐξεπέμφθησαν οἱ πρέσβεις. παραγενομένων δὲ'),
        (10,'IIII Vocans itaque',292,'Claudius reply and introduction to letter; IIII is source text.','2. Καλέσας δὲ Κλαύδιος τοὺς πρέσβεις'),
        (11,'Claudius caesar germanicus',292,'Full imperial titulature and greeting.','Κλαύδιος Καῖσαρ Γερμανικὸς δημαρχικῆς'),
        (12,'Agrippa meo piissimo',292,'Agrippa presentation, garment request, consent and Vitellius precedent.','παντὶ ἔθνει χαίρειν. Ἀγρίππα τοῦ ἐμοῦ'),
        (13,'Huic itaque uoluntati',292,'Religious custom and royal friendships motivate consent; Latin completes the statement.','Οὐιτέλλιος ἐποίησεν. συγκατεθέμην δὲ'),
        (14,'Scripsi uero ob hanc',292,'Writing to Fadus, messengers and date; variant names/date retained.','κρατίστους ὄντας κἀμοὶ τιμίους. ἔγραψα δὲ'),
        (15,'Petiit autem claudio',293,'Herod obtains temple and priestly appointment power; own Latin num15 despite Greek container num13.','3. Ἠιτήσατο δὲ καὶ Ἡρώδης'),
        (16,'Ex illo autem fuit',293,'Power remains in descendants and Cantherius replaced by Joseph.','ἐπέτυχεν. ἐξ ἐκείνου τε πᾶσι'),
        (17,'Eo siquidem tempore',293,'Helena and Izates conversion introduction.','II.1 Κατὰ τοῦτον δὲ τὸν καιρὸν'),
        (18,'Monobazus ad iabenorum',293,'Monobazus marriage and entire dream oracle, not split at pregnancy.','μετέβαλον διὰ τοιαύτην αἰτίαν· Μονόβαζος'),
        (19,'Qua uocetur turbatus',293,'Waking, telling wife and naming son.','τευξόμενον. ταραχθεὶς οὖν ὑπὸ τῆς φωνῆς'),
        (20,'Habebat autem ex helena',293,'Other children and preference for Izates.','Ἰζάτην ἐπεκάλεσεν. ἦν δὲ αὐτῷ Μονόβαζος'),
        (21,'Pro quare ille',293,'Brothers envy and hatred of preference.','ἔχων φανερὸς ἦν. φθόνος δὲ τοὐντεῦθεν'),
        (22,'Hoc pater apertae',293,'Father excuses brothers and sends Izates to Abennirigus; complete continuation checked on p280.','τὰῦτα δὲ καίπερ σαφῶς αἰσθανόμενος')])
