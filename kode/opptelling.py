"""
Leser nedlastede grunnlagsdata NVDB objekt 5 rekkverk i hht Vianova-oppskrift. 

TODO: 
 - Dobbeltsjekk trafikkarbeid-definisjonen, at det er per dag og ikke per år
 

"""
from datetime import datetime
import pandas as pd
import numpy as np
import geopandas as gpd
import STARTHER
import nvdbgeotricks 

def tellRekkverk( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', excelfil=None, returnerdata=None  ): 
    """
    Teller opp rekkverk for inntektsfordeling og returnerer dataFrame med 
    antall og lengde rekkverk i hht reglene 
    """
    rekk = gpd.read_file( grunnlagsdata, layer='rekkverk')
    # rekk = gpd.read_file( '../grunnlagsdata/testdata_tokommunner/grunnlagsdata_TEST.gdb', layer='rekkverk')

    # Tydeliggjør manglende verdi for Bruksområde og Eier
    rekk['Bruksområde'] = rekk['Bruksområde'].fillna( 'IKKE REGISTRERT bruksområde' )
    rekk['Eier'] = rekk['Eier'].fillna( 'IKKE REGISTRERT Eier' )

    # Jada, vi skal kun ha tatt ut objekter på fylkesveg, men filtrerer for sikkerhets skyld
    rekk = rekk[ rekk['vegkategori'] == 'F']

    # Kun trafikantgruppe = K (kjørende)
    rekk = rekk[ rekk['trafikantgruppe'] == 'K']

    # # Filtrerer på bruksområde, inklusive manglende data
    # bruksFilter = [ 'Belysning bru', 'Belysning ferjeleie', 'Belysning gangfelt', 'Belysning område/plass', 'Belysning skilt', 
    #             'Belysning veg/gate', 'Belysning vegkryss', 'IKKE REGISTRERT bruksområde']
    # rekk = rekk[ rekk['Bruksområde'].isin( bruksFilter )]

    # Filtrerer på eier, inklusive manglende data
    eierFilter =  [ 'Fylkeskommune', 'Stat, Statens vegvesen', 'IKKE REGISTRERT Eier' ]
    rekk = rekk[ rekk['Eier'].isin( eierFilter )]

    uten_lengde = rekk[ rekk['Lengde'].isnull()].copy()
    uten_lengde.rename( columns={'segmentlengde' : 'Lengde langs vegnett'}, inplace=True )
    med_lengde = rekk[ ~rekk['Lengde'].isnull()].copy()
    med_lengde = med_lengde.drop_duplicates( subset='nvdbId' )
    med_lengde.rename( columns={'Lengde' : 'LengdeEgenskap'}, inplace=True )
    agg_med_lengde = med_lengde.groupby( 'fylke').agg( {'LengdeEgenskap' : 'sum' } ).reset_index()
    agg_uten_Lengde = uten_lengde.groupby( 'fylke').agg( {'Lengde langs vegnett' : 'sum'} ).reset_index()
    joined = pd.merge( agg_med_lengde, agg_uten_Lengde, on='fylke', how='inner')
    joined['Rekkverk (lm)'] = (joined['LengdeEgenskap'] + joined['Lengde langs vegnett']  )

    resultat = joined[['fylke', 'Rekkverk (lm)']]

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, [resultat, joined, med_lengde, uten_lengde],
                                 sheet_nameListe = ['Ferdige tall', 'Detaljer summering', 
                                                    'Med lengdeegenskap', 'Uten lengdeegenskap'] )

    if returnerdata: 
        return  { 'resultat' : resultat, 'rekkverk_med_lengde' : med_lengde, 'rekkverk_uten_lengde' : uten_lengde }
    else: 
        return resultat 

def tellbelysning( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', excelfil=None, returnerdata=None ): 
    """
    Teller opp belysningspunkt for inntektsfordeling og returnerer dataFrame med 
    antall belysningspunkt i dagen i hht reglene 
    """
    lysGdf = gpd.read_file( grunnlagsdata, layer='belysningspunkt')
    # lysGdf = gpd.read_file( '../grunnlagsdata/testdata_tokommunner/grunnlagsdata_TEST.gdb', layer='belysningspunkt')

    # Tydeliggjør manglende verdi for Bruksområde og Eier
    lysGdf['Bruksområde'] = lysGdf['Bruksområde'].fillna( 'IKKE REGISTRERT bruksområde' )
    lysGdf['Eier'] = lysGdf['Eier'].fillna( 'IKKE REGISTRERT Eier' )

    # Jada, vi skal kun ha tatt ut objekter på fylkesveg, men filtrerer for sikkerhets skyld
    lysGdf = lysGdf[ lysGdf['vegkategori'] == 'F']

    # Kun trafikantgruppe = K (kjørende)
    lysGdf = lysGdf[ lysGdf['trafikantgruppe'] == 'K']


    # Filtrerer på bruksområde, inklusive manglende data
    bruksFilter = [ 'Belysning bru', 'Belysning ferjeleie', 'Belysning gangfelt', 'Belysning område/plass', 'Belysning skilt', 
                'Belysning veg/gate', 'Belysning vegkryss', 'IKKE REGISTRERT bruksområde']
    lysGdf = lysGdf[ lysGdf['Bruksområde'].isin( bruksFilter )]

    # Filtrerer på eier, inklusive manglende data
    eierFilter =  [ 'Fylkeskommune', 'Stat, Statens vegvesen', 'IKKE REGISTRERT Eier' ]
    lysGdf = lysGdf[ lysGdf['Eier'].isin( eierFilter )]

    resultat = lysGdf.groupby( 'fylke').agg( {'nvdbId' : 'count'}).reset_index( )
    resultat.rename( columns={'nvdbId' : 'Lyspunkt i dagen (antall)'}, inplace=True )

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, [resultat, lysGdf ], 
                                 sheet_nameListe=['Ferdige tall', 'filtrert datagrunnlag' ] )

    if returnerdata: 
        return  { 'resultat' : resultat, 'belysning' : lysGdf }
    else: 
        return resultat 



def tellfelt( feltoversikt:str ):
    """
    INTERN FUNKSJON, Teller kjørefelt. Ignorerer ferjeoppstillingsplass (O), svingefelt (H,V) og sykkelfelt (S)
    """
    felt = feltoversikt.split(',')
    count = 0
    for etfelt in felt:
        if 'O' in etfelt or 'H' in etfelt or 'V' in etfelt or 'S' in etfelt:
            pass
        else:
            count += 1
    return count


def tellFeltlengde( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None, returnerdata=None ): 
    """
    Teller feltlengde ihht nye regler. Nå skal vi IKKE telle med ferje

    Teller adskilte løp = Mot (ettersom det er rett når vi skal telle opp felt)

    Teller ikke konnekteringslenker 
    """
    veg = gpd.read_file( grunnlagsdata, layer='vegnett')

    # Filtrerer på trafikantgruppe
    veg = veg[ veg['trafikantgruppe'] == 'K']

    # Teller kun vegtrase-nivå og teller IKKE konnekteringslenker
    veg = veg[ veg['type'] == 'HOVED']

    # Kjørefelt og feltlengde
    veg['antallFelt'] = veg['feltoversikt'].apply( tellfelt )
    veg['feltlengde'] = veg['lengde'] * veg['antallFelt']

    # Deler datasettet i to: Ferje og ikke ferje
    ikkeFerje = veg[ veg['typeVeg'].isin( ['Enkel bilveg', 'Rampe', 'Kanalisert veg', 'Rundkjøring','Gatetun']) ]
    ferje = veg[ veg['typeVeg'] == 'Bilferje']


    minAgg = ikkeFerje.groupby( ['fylke'] ).agg( {'lengde' : 'sum', 'feltlengde' : 'sum' } ).reset_index()
    minAgg['Lengde vegnett (km)'] = minAgg['lengde'] / 1000
    minAgg['Lengde vegnett (km)'] = minAgg['Lengde vegnett (km)'].astype(int)
    minAgg['Feltlengde (km)']     = minAgg['feltlengde'] / 1000
    minAgg['Feltlengde (km)']     = minAgg['Feltlengde (km)'].astype(int)
    minAgg.drop( columns=['lengde', 'feltlengde'], inplace=True )

    ferjeAgg = ferje.groupby( ['fylke'] ).agg( {'lengde' : 'sum', 'feltlengde' : 'sum' } ).reset_index()
    ferjeAgg['Lengde Bilferje (km)'] = ferjeAgg['lengde'] / 1000
    ferjeAgg['Lengde Bilferje (km)']  = ferjeAgg['Lengde Bilferje (km)'].astype(int)
    ferjeAgg['Feltlengde Bilferje (km)']      = ferjeAgg['feltlengde'] / 1000
    ferjeAgg['Feltlengde Bilferje (km)']      = ferjeAgg['Feltlengde Bilferje (km)'].astype(int)
    ferjeAgg.drop( columns=['lengde', 'feltlengde'], inplace=True )
    

    if gdbfil: 
        ikkeFerje.to_file( gdbfil, layer='ikkeFerje', driver='OpenFileGDB')
        ferje.to_file( gdbfil, layer='ferje', driver='OpenFileGDB')

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, [minAgg, ferjeAgg ], 
                                 sheet_nameListe = ['Feltlengde bilveg', 'Feltlengde bilferje'])

    if returnerdata: 
        return  { 'resultat' : minAgg, 'bilveg' : ikkeFerje, 'bilferje' : ferje }
    else: 
        return minAgg

def tellTrafikk( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None, returnerdata=None ): 
    """
    Regner ut 
      * Trafikkarbeid i millioner kjørte km PER DAG (ikke per år)
      * lengde med ÅDT > 4000 etter KOSTRA-logikk, men vi ser ikke på "adskilte løp"
      (antar at trafikkmengden er ferdig fordelt på de to løpene. Vi har 47 tilfeller og 12km med 
      adskilte løp=Mot). Ideelt sett hadde vi brukt egenskapen "Trafikkmengde på adskilte løp", 
      men der har vi ingen data foreløpig 
    """
    myGdf = gpd.read_file( grunnlagsdata, layer='trafikkmengde')
    myGdf = myGdf[ myGdf['vegkategori'] == 'F']
    myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']

    # KOSTRA-filtrering unntatt dette med adskilte løp
    over4000Gdf = myGdf[ myGdf['ÅDT__total'] > 4000 ]
    over4000Gdf = over4000Gdf[ over4000Gdf['veglenkeType'] == 'HOVED']
    over4000Gdf = over4000Gdf[ ~over4000Gdf['vref'].str.contains( 'SD' ) ]
    # TODO: Implementer logikk for egenskapen "Trafikkmengde på adskilte løp" når det blir data tilgjengelig

    over4000adt = over4000Gdf.groupby( 'fylke' ).agg( {  'segmentlengde'  : 'sum' } ).reset_index()
    over4000adt.rename( columns={'segmentlengde' : 'Lengde Ådt > 4000 (km)'} , inplace=True)
    over4000adt['Lengde Ådt > 4000 (km)'] = over4000adt['Lengde Ådt > 4000 (km)'] / 1000

    # Skal ha kjøretøykm PER DAG og IKKE per år, slik som er vanlig
    # myGdf['kjoretoyKm'] = myGdf['segmentlengde'] * myGdf['ÅDT__total'] * 365 / 1000 # per dag (vanlig ellers i verden)
    myGdf['kjoretoyKm'] = myGdf['segmentlengde'] * myGdf['ÅDT__total']         / 1000 # Multipliserer IKKE med 365
    trafikkArb = myGdf.groupby([ 'fylke'] ).agg( {'segmentlengde' : 'sum', 'kjoretoyKm' : 'sum' } ).reset_index()
    trafikkArb['Trafikkarbeid (mill kjøretøykm)'] = trafikkArb['kjoretoyKm'] / 1e6
    trafikkArb['Lengde veg som har ÅDT-data (km)'] = trafikkArb['segmentlengde'] / 1000
    trafikkArb.drop( columns=['segmentlengde', 'kjoretoyKm'], inplace=True )

    resultat = pd.merge( trafikkArb, over4000adt, on='fylke' ) 

    if gdbfil or excelfil: 
        print( f"Ikke implementert lagring til fil for dette datasettet")

    if returnerdata: 
        return  { 'resultat' : resultat, 'trafikk' : myGdf }
    else: 
        return resultat 


def tellLavFart( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None, returnerdata=None ): 
    """
    Regner ut lengde med fartsgrense <= 50 km/t 
    
    Ignorerer adskilte løp = MOT og konnekteringslenker 
    """
    myGdf = gpd.read_file( grunnlagsdata, layer='fartsgrense')

    # Teller kun fylkesveg (får med objekter med multippel stedfesting på f.eks Sv136 i kommune 3448)
    myGdf = myGdf[ myGdf['vegkategori'] == 'F']

    # Filtrerer på trafikantgruppe, kun kjørende
    myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']

    # Teller kun vegtrase-nivå og teller IKKE konnekteringslenker
    myGdf = myGdf[ myGdf['veglenkeType'] == 'HOVED']

    # Ikke adskilte løp = Mot. Dette utgjør 12 km. 
    myGdf = myGdf[ myGdf['adskilte_lop'] != 'Mot']

    # Ikke sideanlegg. Dette utgjør 87 km i 2024. 
    myGdf = myGdf[ ~myGdf['vref'].str.contains( 'SD' ) ]

    # Kun disse veglenketypene
    KostraTypeVeg = ['Enkel bilveg', 'Kanalisert veg', 'Rundkjøring', 'Rampe', 'Gatetun']
    myGdf = myGdf[ myGdf['typeVeg'].isin( KostraTypeVeg )]

    # Kun fartsgrense 50 km/t eller lavere
    under50 = myGdf[ myGdf['Fartsgrense'] <= 50 ].groupby( 'fylke' ).agg( {  'segmentlengde'  : 'sum' } ).reset_index()
    under50navn = 'Veg med fartsgrense 50 km/t eller lavere (km)'
    under50[under50navn] = under50['segmentlengde'] / 1000

    if gdbfil or excelfil: 
        print( f"Ikke implementert lagring til fil for fartsgrense < 50 km/t")

    resultat = under50[['fylke', under50navn]]

    if returnerdata: 
        return  { 'resultat' : resultat, 'under50' : myGdf }
    else: 
        return resultat 


def __finnLengdeLop( row ):
    """
    Intern funksjon som plukker ut sum lengde alle løp fra tunnel-objektet
    Hvis den ikke finnes så brukes "Lengde, offisiell"

    Merk at dette er stikk MOTSATT av all annen bruk av "Lengde, offisiell".
    """
    if np.isnan( row['Sum_lengde_alle_løp'] ):
        return row['Lengde__offisiell']
    else:
        return row['Sum_lengde_alle_løp']


def tellTunnel( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None, returnerdata=None ): 
    """
    Teller tunnelløp
    """

    myGdf = gpd.read_file( grunnlagsdata, layer='tunnel')

    myGdf['Lengde'] = myGdf.apply( __finnLengdeLop, axis=1)

    myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']

    undersjoisk = myGdf[ myGdf['Undersjøisk'] == 'Ja'].groupby( 'fylke' ).agg( { 'Lengde' : 'sum' } ).reset_index()
    landtunnel = myGdf[ myGdf['Undersjøisk'] != 'Ja'].groupby( 'fylke' ).agg( { 'Lengde' : 'sum' } ).reset_index()

    undersjoisk.rename( columns={ 'Lengde' : 'Lengde undersjøiske tunnelløp (m)' }, inplace=True )
    landtunnel.rename( columns={ 'Lengde' : 'Lengde ikke-undersjøiske tunnelløp (m)' }, inplace=True )
    resultat = pd.merge( landtunnel, undersjoisk, on='fylke', how='left' )

    if gdbfil: 
        print( f"Ikke implementert lagring til FGDB for tunneldata")

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, myGdf )
        
    if returnerdata: 
        return  { 'resultat' : resultat, 'tunneler' : myGdf }
    else: 
        return resultat

def tellGangsykkel( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None ): 
    """
    Teller gang- og sykkelveg for de tre veglenketypene Gangveg, Gang- og sykkelveg, Sykkelveg. 

    Tidligere har vi kun telt Gang- og sykkelveg. 
    """

    myGdf = gpd.read_file( grunnlagsdata, layer='vegnett')
    myGdf = myGdf[ myGdf['typeVeg'].isin( ['Gang- og sykkelveg', 'Sykkelveg', 'Gangveg'] )]
    myGdf['Lengde sykkel- og gangveger [km]'] = myGdf['lengde'] / 1000
    gstall = myGdf.groupby( 'fylke').agg( {'Lengde sykkel- og gangveger [km]' : 'sum'} ).reset_index()

    if gdbfil: 
        myGdf.to_file( gdbfil, layer='Sykkel og gangveger', driver='OpenFileGDB')

    if excelfil: 
        print( f"Ikke implementert lagring til Excel for telling av gang- og sykkelveger")

    return gstall 

def tellAltOmBruer_NVDBdata( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', gdbfil=None, excelfil=None, returnerdata=None): 
    """
    Teller opp ferjekaier og tilleggskaier som er registert i NVDB

    Foretrekker EGENTLIG at disse dataene kommer fra Brutus 
    """

    myGdf = gpd.read_file( grunnlagsdata, layer='bru')

    # Filtrerer på status. Merk mellomrom bakerst i varianten "Trafikkert "
    myGdf['Status'] = myGdf['Status'].fillna( '--BLANK--' )
    statusliste = ['Trafikkert ', '--BLANK--']
    myGdf = myGdf[ myGdf['Status'].isin( statusliste )]    

    # ferjekaier
    # Disse byggverktypene er definert i oppskriften: 810, 811, 812, 820, 822, 823, 824. 
    # Merk at vi hopper over 821. 
    disseByggverkTypene = ['Ferjekaibru (810)', 'Ferjekaibru (811)', 'Ferjekaibru (812)', 'Kai (820)', 'Tilleggskai (822)',  'Tilleggskai (823)', 'Tilleggskai (824)' ]
    # Andre varianter av Byggverkstype jeg finner  i dataene, men som ikke er med i oppskriften 
    #  ['Tilleggskai (821)', 'Ferjekaibru (819)',   'Liggekai (826)', 'Liggekai (827)', 'Ro-Ro-rampe (828)' 

    ferjekaiGdf = myGdf[ myGdf['Byggverkstype'].isin( disseByggverkTypene )]
    ferjekaiGdf = ferjekaiGdf.drop_duplicates( subset='nvdbId')
    ferjekai = ferjekaiGdf.groupby( 'fylke' ).agg( {'nvdbId' : 'count' }).reset_index()
    ferjekai.rename( columns={'nvdbId': 'Ferjekaibruer og tilleggskaier (antall)'}, inplace=True )

    # Bruer
    vegbruGdf = myGdf[ myGdf['Brukategori'].isin([ 'Bru i fylling', 'Vegbru' ]) ]
    vegbruGdf = vegbruGdf.drop_duplicates( subset='nvdbId')

    lengde_staal = vegbruGdf[vegbruGdf['Materialtype'] == 'Stål'].groupby( ['fylke']).agg( 
        {'Lengde' : 'sum'}).reset_index()
    lengde_ikke_staal = vegbruGdf[vegbruGdf['Materialtype'] != 'Stål'].groupby( ['fylke']).agg( 
        {'Lengde' : 'sum'}).reset_index()

    lengde_staal.rename( columns={'Lengde' : 'Lengde bruer av stål (m)'}, inplace=True )
    lengde_ikke_staal.rename( columns={'Lengde' : 'Lengde bruer av andre materialtyper enn stål (m)' }, inplace=True )

    tmp = pd.merge( lengde_staal, lengde_ikke_staal, on='fylke', how='left')
    resultat = pd.merge( tmp, ferjekai, how='left', on='fylke')
    resultat['fylke'] = resultat['fylke'].astype(int)

    if gdbfil: 
        pass
        # myGdf.to_file( gdbfil, layer='Sykkel og gangveger', driver='OpenFileGDB')

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, [vegbruGdf, ferjekaiGdf],  
                        sheet_nameListe = ['Vegbru', 'Ferjekai og tillegskai'])
  
    if returnerdata: 
        return  { 'resultat' : resultat, 'vegbruer' : vegbruGdf, 'ferjekaitillegg' : ferjekaiGdf }
    else: 
        return resultat
    
def fylkesnavn( ):
    """
    Returnerer dataframe med fylke = fylkesnummer og Fylkesnavn
    """ 
    fylker = [  { 'fylke' : 11 , 'Fylkesnavn' : 'Rogaland' },
                { 'fylke' : 15 , 'Fylkesnavn' : 'Møre og Romsdal' },
                { 'fylke' : 18 , 'Fylkesnavn' : 'Nordland' },
                { 'fylke' : 31 , 'Fylkesnavn' : 'Østfold' },
                { 'fylke' : 32 , 'Fylkesnavn' : 'Akershus' },
                { 'fylke' : 33 , 'Fylkesnavn' : 'Buskerud' },
                { 'fylke' : 34 , 'Fylkesnavn' : 'Innlandet' },
                { 'fylke' : 39 , 'Fylkesnavn' : 'Vestfold' },
                { 'fylke' : 40 , 'Fylkesnavn' : 'Telemark' },
                { 'fylke' : 42 , 'Fylkesnavn' : 'Agder' },
                { 'fylke' : 46 , 'Fylkesnavn' : 'Vestland' },
                { 'fylke' : 50 , 'Fylkesnavn' : 'Trøndelag' },
                { 'fylke' : 55 , 'Fylkesnavn' : 'Troms' },
                { 'fylke' : 56 , 'Fylkesnavn' : 'Finnmark' }  ]

    return pd.DataFrame( fylker)
    
def telloppalt(  grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', gdbfil=None, excelfil=None ):
    """
    Teller opp alle fylkesveg-kriteriedata
    """
    t0 = datetime.now()
    mydir = '../resultater/mellomregning/'

    print( f"Tar cirka en halvtime")
    fylker = fylkesnavn()
    print( f"ca 6 min: feltlengde"); feltlengde = tellFeltlengde(       grunnlagsdata=grunnlagsdata )
    print( f"ca 1 min: trafikk"   ); trafikk = tellTrafikk(             grunnlagsdata=grunnlagsdata )       # trafikkarbeid og ÅDT > 4000 
    print( f"ca 4 min: rekkverk"  ); rekkverk = tellRekkverk(           grunnlagsdata=grunnlagsdata, excelfil=mydir+'rekkverk.xlsx')
    print( f"ca 6 min: lyspunkt"  ); lyspunkt = tellbelysning(          grunnlagsdata=grunnlagsdata, excelfil=mydir+'lyspunkt.xlsx')
    print( f"ca 1 min: tunnel"    ); tunnel = tellTunnel(               grunnlagsdata=grunnlagsdata, excelfil=mydir+'tunnel.xlsx' ) # Ikke-undersjøisk og undersjøiske tunneller 
    print( f"ca 1 min: bruer"     ); bruer = tellAltOmBruer_NVDBdata(   grunnlagsdata=grunnlagsdata, excelfil=mydir+'bruer.xlsx' )
    print( f"ca 9 min: G/S"       ); sykkel = tellGangsykkel(           grunnlagsdata=grunnlagsdata )
    print( f"ca 1 min: Fartsg<50" ); fart50 = tellLavFart(              grunnlagsdata=grunnlagsdata )

    myDfList = [ fylker, feltlengde, trafikk, rekkverk, lyspunkt, tunnel, bruer, sykkel,  fart50 ] 
    myDfList = [ df.set_index( 'fylke') for df in myDfList ]
    FERDIG = pd.concat( myDfList, axis=1 ).reset_index()
    FERDIG['fylke'] = FERDIG['fylke'].astype(int)

    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, FERDIG ) 

    # from IPython import embed; embed()
    print( f"Tidsbruk opptelling: {datetime.now()-t0}")
    return FERDIG 

def sammenlignLeveranse( filnavn:str, nyLeveranse:str, gammelLeveranse:str, nyFylkeKolonne='fylke', gammelFylkekolonne='Fylkesnr 2024'): 
    """
    Sammenligner fjorårets leveranse med det du har produsert. Lager nytt regneark med en fane per variabel 

    ARGUMENTS
        filnavn : Navn på den nye excel-fila

        nyLeveranse : Filnavn på den nye rapporten 

        gammelLeveranse : Filnavn på den gamle rapportne 

    KEYWORDS
        nyFylkeKolonne = 'fylke' Navn på kolonnen som inneholder fylkesnummer i den nye leveransen

        gammelFylkeKolonne = 'Fylkesnr 2024' Navn på kolonnen som inneholder fylkesnummer i den nye leveransen

    RETURNS
        None     
    """

    nytt = pd.read_excel( nyLeveranse )
    nytt = nytt.add_prefix( 'NY '  )
    nytt = nytt.rename( columns={'NY fylke' : 'fylke'} )

    gammalt = pd.read_excel( gammelLeveranse )
    if gammelFylkekolonne != 'fylke': 
        gammalt.rename( columns={gammelFylkekolonne : 'fylke'}, inplace=True )

    nyeKolonner = nytt.columns
    gamleKolonner = gammalt.columns 

    dataframes = [nytt, gammalt]
    
    joined = pd.merge( nytt, gammalt, how='left', on='fylke')
    if 'NY Fylkesnavn' in joined.columns: 
        joined = joined.drop( columns='NY Fylkesnavn' )

    differanser = joined[['fylke', 'Fylkesnavn']].copy()
    
    parametre = [ x for x in gammalt.columns if x not in ['fylke', 'Fylkesnavn', 'Lengde vegnett (km)'] ]
    for p in parametre:
        nyP = 'NY ' + p 

        # Har byttet navn for å signalisere historikkbrudd:
        if p == 'G/S-veglengde (km)': 
            nyP = 'NY Lengde sykkel- og gangveger [km]'

        if nyP in joined.columns: 
            temp = joined[['fylke', 'Fylkesnavn', nyP, p]].copy()
            temp['differanse'] = temp[nyP] - temp[p]
            temp['Prosentvis endring %'] = round( (temp['differanse'] * 100)  / temp[p], 2 )
            differanser[nyP[3:]]               = temp[nyP]
            differanser['Endring ' + nyP[3:] ] = temp['differanse']
            differanser['Prosent ' + nyP[3:] ] = temp['Prosentvis endring %']
        else: 
            print( f"Parameter {p} ikke funnet i nytt datasett")

    dataframes.append( differanser )

    nvdbgeotricks.skrivexcel( filnavn, differanser, sheet_nameListe=['Differanser'])

def lagSammenligning( filnavn='Sammenligning fjorårets grunnlagsdata.xlsx'):
    """
    Hardkoding av filnavn for årets og fjorårets leveranse. 

    Bruker funksjonen sammenlignLeveranse
    """
    nytt = '../resultater/Grunnlagsdata-inntekt-fylkeskommune2025.xlsx'
    gammaltDir = '../resultater/resultatFraIfjor/'
    gammalt = gammaltDir+'REVIDERTE Grunnlagsdata-inntekt-Fylkeskommunene2024.xlsx'

    sammenlignLeveranse( filnavn, nytt, gammalt)
    

if __name__ == '__main__':
    # print( "Opptelling belysningspunkt i dagen\n", tellbelysning()  )      # ca 6 minutt
    # print( "Opptelling rekkverk\n",                tellRekkverk()   )      # ca 4 minutt
    # print( "Opptelling feltlengde",                tellFeltlengde() )      # ca 9 minutt
    # print( "Opptelling trafikkmengde\n",           tellTrafikk()    )      # ca 1 minutt
    # print( "Opptelling fartsgrense <= 50 km/t\n",  tellLavFart()    )      # ca 1 minutt
    # print( "Opptelling tunneller\n",               tellTunnel()    )       # Raskt 
    # print( "Opptelling G/S veg\n",                 tellGangsykkel()    )   # ca 9 minutt
    # print( "Opptelling bruer fra NVDB\n",   tellAltOmBruer_NVDBdata()  )   # ca 17 sekund

    FERDIG = telloppalt( excelfil='../resultater/Grunnlagsdata-inntekt-fylkeskommune2025.xlsx')
    lagSammenligning(filnavn='../resultater/resultatFraIfjor/Sammenligning fjorårets resultater.xlsx')