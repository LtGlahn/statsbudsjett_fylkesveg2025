"""
Leser nedlastede grunnlagsdata NVDB objekt 87 belysningspunkt og fordeler på 
belysningspunkt i dagen og belysningspunkt i tunnell, i hht Vianova-oppskrift. 
"""
import geopandas as gpd
import STARTHER
import nvdbgeotricks 

def tellbelysning( excelfil=None ): 
    """
    Teller opp belysningspunkt for inntektsfordeling og returnerer dataFrame med 
    antall belysningspunkt i dagen i hht reglene 
    """
    # lysGdf = gpd.read_file( '../grunnlagsdata/grunnlagsdata.gdb', layer='belysningspunkt')
    lysGdf = gpd.read_file( '../grunnlagsdata/testdata_tokommunner/grunnlagsdata_TEST.gdb', layer='belysningspunkt')

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
        nvdbgeotricks.skrivexcel( excelfil, resultat )
    return resultat 

if __name__ == '__main__':
    tellbelysning()


