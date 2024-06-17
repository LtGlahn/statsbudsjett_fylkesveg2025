# statsbudsjett_fylkesveg2025
Tar ut vegnett og en håndfull vegobjekter til budsjettfordeling fylkesveg 2025



### Feltlengde

For budsjettåret 2025 så skal vi ikke lenger teller feltlengde for bilferje lenger.Vi teller heller ikke med konnekteringslenker. Det betyr at vi regner ut feltlengde for veglenketypene Enkel bilveg, Rampe, Kanalisert veg, Rundkjøring og Gatetun. 

Endringene for budsjettåret 2025 ser ut til å være konsistente med frafall av bilferjer pluss en liten justering. 

### Lengde Undersjøiske og Ikke-undersjøiske tunneller  

Vi summerer lengden registrert på NVDB objekttype 581 Tunnel. Aller helst bruker vi egenskapen "Sum lengde alle løp", men for 20 av tunnelobjektene mangler vi denne egenskapverdien, og for dem bruker vi i stedet egenskapen "Sum lengde alle løp". 

Sju av tunnellene er for gående og syklende (trafikantgruppe G), og telles ikke med. Ved senere revisjon bør vi diskutere om vi også skal inkludere tunneller for syklende og gående. 

Siden i fjor er det kommet til tre nye tunneller: 
  * Rogaland: Byhaugtunnelen (777 meter) har byttet vegkategori, fra europaveg til fylkesveg 
  * Møre og Romsdal: Indreeidstunellen (4892 meter)
  * Troms: Svartholla II (99 meter) 

I tillegg var det en tunnel i Vestland fylke der det en periode i 2023 var en registreringsfeil som medførte at Agjeldstunnelen (961 meter)  ble regnet som undersjøisk tunnel da vi tok ut inntektsgrunnlag sommeren 2023. Datafeilen ble korrigert i NVDB senere samme år, mer presist har egenskapen  `Undersjøisk = Ja` blitt korrigert til verdien  `Nei`. Dette er årsaken til at Vestland fylke for inntektsgrunnlag 2025 har 961 meter mindre undersjøisk og 961 meter mere ikke-undersjøisk tunnel enn i fjor.

### Trafikkarbeid (millioner kjøretøykm)

_...to be written..._ 

### Lengde veg med ÅDT over 4000 kjøretøy per døgn

_...to be written..._ 


### Lengde rekkverk (løpemeter)

_...to be written..._ 


### Lyspunkt i dagen 

_...to be written..._ 

### Lengde bruer av stål og bruer av andre materialtyper enn stål 

_...to be written..._ 


### Ferjekaibru og tillegskai

Disse dataene ajourholdes i Brutus, som også fortløpende oppdaterer objekttypen "60 Bru" i NVDB. Her følger vi den såkalte  [Vianova-oppskriften fra 2021](https://www.regjeringen.no/contentassets/e8645ebe0e02470da89253caef0addba/rapport-forenklet-modell-til-kriteriet-for-utgiftsbehov-ti1405835.pdf)

som beskriver filtre for datauttak av NVDB-objekt av typen 60 bru på fylkesveg:
  * vegsystemreferanse = Fv
  * trafikantgruppe = 'K'

Og filtrert på disse egenskapene:
  * Brukategori = Ferjeleie 
  * Status = Trafikkert, (blank) 
  * Byggverkstype skal være én av disse: 
    * Ferjekaibru (810)
    * Ferjekaibru (811)
    * Ferjekaibru (812)
    * Kai (820)
    * Tilleggskai (822)
    * Tilleggskai (823)
    * Tilleggskai (824)

Merk at egenskapsfilteret `Byggverkstype' dermed også ekskluderer  variantene: 
  * Tilleggskai (821)
  * Ferjekaibru (819)
  * Liggekai (826)
  * Liggekai (827) 
  * Ro-Ro-rampe (828)

Vi er ikke kjent med det faglige grunnlaget for at Vianova-oppskriften eksluderer disse fem byggverkstypene, og mener dette burde vært revidert. 

For datauttaket til statsbudsjett 2025 ser vi at vi har en reduksjon på 8 stykk ferjekaibru og tilleggskai i forhold til i fjor. Vi har tatt stikkprøver for fem av dem: Ett objekt [392903643](http://vegkart.atlas.vegvesen.no/#valgt:392903643:60) ligger på vegnett som er satt historisk pga fysisk ombygging. De fire andre har fått egenskapverdien `Byggverkstype = Ferjekaibru (819)`, som IKKE skal regnes med når vi følger Vianova-oppskriften slavisk. 

# Lengde gangveg, sykkelveg og gang- og sykkelveg

Tidligere har vi kun talt opp veglenketypen _Gang og sykkelveg_.  Fra og med i år skal vi også telle med veglenketypene _Gangveg_ og _Sykkelveg_. Dette er nye veglenketyper som vi tidligere har manglet data på, men som nå gradvis blir registrert i NVDB. 

Tallene for foregående års inntekstgrunnlag er derfor ikke direkte sammenlignbare, ettersom de kun talte _Gang og sykkelveg_. I tillegg jobber både Kartverket og Statens vegvesen med å få registrert manglende data på disse veglenketypene, så årets data er ikke nødvendigvis komplette.  

![Skiltnummer 522 gang og sykkelveg](./pics/skiltnummer522.png)


### Veg med fartsgrense 50 km/t eller lavere

Her følger vi KOSTRA-metodikk for å telle veg: _Vi teller alle kryssdeler, men ikke sideanlegg, konnekteringslenker eller adskilte løp=MOT. Og vi teller kun veglenketypene kanalisertVeg, enkelBilveg, rampe, rundkjøring og gatetun_. 