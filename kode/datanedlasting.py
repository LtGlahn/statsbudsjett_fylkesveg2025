"""
Laster ned data fra NVDB api LES og lagrer til disk 

Analysen blir mer etterprøvbar når vi har stålkontroll på datagrunnlaget. NVDB er en høyst levende
database med daglige endringer. Det kan dermed være krevende å ettergå analyser når NVDB vegnett og
datagrunnlag kan ha endret seg.
"""
import pandas as pd
import geopandas as gpd
from shapely import wkt 


import STARTHER
import nvdbapiv3
import nvdbgeotricks

def lagreData( sokeobjekt, gdbfil, layer, excelfil=None ):
    """
    Lagrer søkeobjekt NVDB til fil-geodatabase (og evt også som excelfil)

    ARGUMENTS: 
        sokeobjek - nvdbapiv3.nvdbVegnett() eller nvdbapiv3.nvdbFagdata søkeobjekt 

        gdbfil - navn på fil-geodatabase der vi skal lagre data

        layer - Lagnavn som brukes når vi lagrer til filgeodatabase

    KEYWORDS
        excelfil=None | txt, filnavn hvis vi skal lagre excelfil 

    RETURNS
        None 
    """
    
    mydf = pd.DataFrame( sokeobjekt.to_records() )
    myGdf = gpd.GeoDataFrame( mydf, geometry=mydf['geometri'].apply( wkt.loads ), crs=5973 )
    myGdf.to_file( datafil, layer=layer, driver='OpenFileGDB' )
    if excelfil: 
        nvdbgeotricks.skrivexcel( excelfil, mydf )


    # Verifiser at vi har riktig antall 
    testGdf = gpd.read_file( gdbfil, layer=layer )
    if len( testGdf ) != len( mydf ): 
        raise( ValueError( "Avvik antall lagret på disk - arbeidsminne!"))

if __name__ == '__main__': 

    # mappe og filer der vi lagrer grunnlagsdata
    datadir = '../grunnlagsdata/'
    datafil =  datadir + 'grunnlagsdata.gdb'

    mittfilter = { 'vegsystemreferanse' : 'Fv' }

    # testdata for utvikling: Kun data innfafor Vestvågøy og Vågan kommune
    # mittfilter['kommune'] = 1860,1865

    # Lagrer vegnett 
    lagreData( nvdbapiv3.nvdbVegnett( filter=mittfilter ), datafil, 'vegnett', datadir+'grunnlagsdata_vegnett.xlsx' )

    # Lagrer Belysningspunkt 
    lagreData( nvdbapiv3.nvdbFagdata(87, filter=mittfilter ), datafil, 'belysningspunkt', datadir+'grunnlagsdata_belysningspunkt.xlsx' )

    # Lagrer rekkverk 
    lagreData( nvdbapiv3.nvdbFagdata(5, filter=mittfilter ), datafil, 'rekkverk', datadir+'grunnlagsdata_rekkverk.xlsx' )


    # Lagrer bruobjekter (som også omfatter ferjekaier og VELDIG mye mer)
    # Uavklart: Er det NVDB eller Brutus (foretrukket) som skal væe fasiten på antall ferjekaier og bruer til stadsbudsett? 
    lagreData( nvdbapiv3.nvdbFagdata(60, filter=mittfilter ), datafil, 'bru', datadir+'grunnlagsdata_bru.xlsx' )
    
    # Lagre fartsgrenser. Tar alt, enklere å filtrere etterpå. 
    lagreData( nvdbapiv3.nvdbFagdata(105, filter=mittfilter ), datafil, 'fartsgrense', datadir+'grunnlagsdata_fartsgrense.xlsx' )

    # Tunnel
    lagreData( nvdbapiv3.nvdbFagdata(581, filter=mittfilter ), datafil, 'tunnel', datadir+'grunnlagsdata_tunnel.xlsx' )


    # Trafikkmengde
    lagreData( nvdbapiv3.nvdbFagdata(540, filter=mittfilter ), datafil, 'trafikkmengde', datadir+'grunnlagsdata_trafikkmengde.xlsx' )

