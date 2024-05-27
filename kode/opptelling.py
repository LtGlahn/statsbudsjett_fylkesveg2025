"""
Leser nedlastede grunnlagsdata NVDB objekt 5 rekkverk i hht Vianova-oppskrift. 
"""
import pandas as pd
import geopandas as gpd
import STARTHER
import nvdbgeotricks 

def tellRekkverk( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', excelfil=None ): 
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
    return resultat 

def tellbelysning( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb', excelfil=None ): 
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
    return resultat 


def tellfelt( feltoversikt:str ):
    """
    Teller kjørefelt. Ignorerer ferjeoppstillingsplass (O), svingefelt (H,V) og sykkelfelt (S)
    """
    felt = feltoversikt.split(',')
    count = 0
    for etfelt in felt:
        if 'O' in etfelt or 'H' in etfelt or 'V' in etfelt or 'S' in etfelt:
            pass
        else:
            count += 1
    return count


def tellFeltlengde( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None ): 
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

    return minAgg

def tellTrafikk( grunnlagsdata='../grunnlagsdata/grunnlagsdata.gdb',  gdbfil=None, excelfil=None ): 
    """
    Regner ut lengde med ÅDT > 1500 
    """
    myGdf = gpd.read_file( grunnlagsdata, layer='trafikkmengde')
    myGdf = myGdf[ myGdf['trafikantgruppe'] == 'K']

    over1500adt = myGdf[ myGdf['ÅDT__total'] > 1500 ].groupby( 'fylke' ).agg( {  'segmentlengde'  : 'sum' } ).reset_index()
    over1500adt.rename( columns={'segmentlengde' : 'Lengde Ådt > 1500 (km)'} , inplace=True)
    over1500adt['Lengde Ådt > 1500 (km)'] = over1500adt['Lengde Ådt > 1500 (km)'] / 1000

    # Skal ha kjøretøykm PER DAG og IKKE per år, slik som er vanlig
    # myGdf['kjoretoyKm'] = myGdf['segmentlengde'] * myGdf['ÅDT__total'] * 365 / 1000 # per dag (vanlig ellers i verden)
    myGdf['kjoretoyKm'] = myGdf['segmentlengde'] * myGdf['ÅDT__total']         / 1000 # Multipliserer IKKE med 365
    trafikkArb = myGdf.groupby([ 'fylke'] ).agg( {'segmentlengde' : 'sum', 'kjoretoyKm' : 'sum' } ).reset_index()
    trafikkArb['Trafikkarbeid (mill kjøretøykm)'] = trafikkArb['kjoretoyKm'] / 1e6
    trafikkArb['Lengde veg som har ÅDT-data (km)'] = trafikkArb['segmentlengde'] / 1000
    trafikkArb.drop( columns=['segmentlengde', 'kjoretoyKm'], inplace=True )

    resultat = pd.merge( trafikkArb, over1500adt, on='fylke' ) 

    if gdbfil or excelfil: 
        print( f"Ikke implementert lagring til fil for dette datasettet")

    return resultat


if __name__ == '__main__':
    print( "Opptelling belysningspunkt i dagen\n", tellbelysning() )
    print( "Opptelling rekkverk\n",                tellRekkverk() )
    print( "Opptelling feltlengde",                tellFeltlengde() )
    print( "Opptelling trafikkmengde\n",           tellTrafikk() )


    
