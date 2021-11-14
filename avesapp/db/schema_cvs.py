import csv
import sqlite3
import pprint

pp = pprint.PrettyPrinter( indent=4, width=80 )

def main():
    con = sqlite3.connect( 'db_test1.db' )
    con.row_factory = sqlite3.Row
    
    c = con.cursor()

    with open( 'schema.sql', encoding='utf8' ) as f_schema:
        c.executescript( f_schema.read() )

    con.commit()

    with open( 'avesPEFI.csv', encoding='utf8' ) as f_aves_pefi:
        csv_reader = csv.DictReader( f_aves_pefi, delimiter=';', quotechar='"' )
        for row in csv_reader:
            #pp.pprint( row )

            # Separa nome ciêntifico
            nc_row = row[ 'Nomes científicos' ]
            nome_cientifico = nc_row.strip()
            autor = ''
            nome_comp = nome_cientifico
            if ( autor_pos := nc_row.find( '(' ) ) >= 0:
                nome_cientifico = nc_row[ 0 : autor_pos ].strip()
                autor = nc_row[ autor_pos : ].replace( '(', '' ).replace( ')', '' )
                nome_comp = f"{nome_cientifico} ({autor})"

            #print( 'Nome cinetífico:', nome_cientifico, end='; ' )
            #print( 'Autor:', autor, end='; ' )
            #print( 'Nome comp:', nome_comp, end='; ' )
            #print( )
                

    







    
if __name__ == '__main__':
    main()
