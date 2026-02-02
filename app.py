import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Scanner GLOVO Pro", layout="wide")

def detecter_type(nom):
    nom = str(nom).upper().strip()
    if any(m in nom for m in ["PLATEAU", "PLT"]): return "PLATEAUX"
    if "BOITE" in nom: return "BOITE_BELDI"
    if any(m in nom for m in ["ENTREMET", "ENT"]): return "ENTREMETS"
    if any(m in nom for m in ["CAKE", "MADELEINE", "BROWNIE", "FONDANT"]): return "CAKE"
    if any(m in nom for m in ["CROISSANT","CROIS", "SCHNICK", "PAIN AU CHOCOLAT", "SUISSE", "KRACHEL", "COOKIE", "BEIGNET"]): return "VIENNOISERIE"
    if any(m in nom for m in ["PAIN", "BAGUETTE", "SEMOULE"]): return "BOULANGERIE"
    if any(m in nom for m in ["TARTE", "ECLAIR", "MILLE", "PATISSERIE"]): return "PATISSERIE"
    if any(m in nom for m in ["PIZZA", "QUICHE", "SALÉ", "MSAMEN", "BRIOUATE", "PASTILLA","HARCHA"]): return "SALÉS"
    if any(m in nom for m in ["CALADE", "COFFRET"]): return "A OFRRIRE"
    return "AUTRES"

st.title("🚀 Scanner GLOVO Haute Précision")

file = st.file_uploader("Chargez votre fichier JOURNAL", type=['xlsx'])

if file:
    try:
        # On lit tout le fichier sans en-tête pour ne rien rater
        df_raw = pd.read_excel(file, header=None)
        
        articles = []
        # On scanne chaque ligne pour trouver des données valides
        for i, row in df_raw.iterrows():
            nom = str(row[0]).strip()
            # On cherche une ligne où la 1ère colonne n'est pas vide et la 2ème est un chiffre
            if nom != "" and nom.lower() != "nan" and nom.lower() != "glovo":
                try:
                    # On tente de convertir la 2ème colonne en chiffre
                    v = float(row[1])
                    if not pd.isna(v) and v > 0:
                        articles.append({
                            "Nom": nom,
                            "Vente": v,
                            "Type": detecter_type(nom)
                        })
                except:
                    continue

        if articles:
            full_df = pd.DataFrame(articles)
            
            # --- CRÉATION EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                workbook = writer.book
                ws = workbook.add_worksheet("Rapport")
                
                f_titre = workbook.add_format({'bold': True, 'bg_color': '#FFC000', 'border': 1, 'align': 'center'})
                f_head = workbook.add_format({'bold': True, 'bg_color': '#D9D9D9', 'border': 1})
                f_data = workbook.add_format({'border': 1})

                row_idx = 0
                for t in full_df['Type'].unique():
                    ws.merge_range(row_idx, 0, row_idx, 1, f"TYPE : {t}", f_titre)
                    row_idx += 1
                    ws.write(row_idx, 0, "Produit", f_head)
                    ws.write(row_idx, 1, "Vente", f_head)
                    row_idx += 1
                    
                    sub = full_df[full_df['Type'] == t]
                    for _, r in sub.iterrows():
                        ws.write(row_idx, 0, r['Nom'], f_data)
                        ws.write(row_idx, 1, r['Vente'], f_data)
                        row_idx += 1
                    row_idx += 1

                ws.set_column(0, 0, 45)
                ws.set_column(1, 1, 15)

            # --- AFFICHAGE ---
            st.success(f"✅ Analyse réussie : {len(articles)} articles trouvés !")
            
            st.download_button(
                label="📥 TÉLÉCHARGER LE RÉSULTAT TRIÉ",
                data=output.getvalue(),
                file_name="GLOVO_TRIE_FINAL.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.write("### Aperçu des données trouvées :")
            st.dataframe(full_df)

        else:
            st.warning("⚠️ Fichier reçu, mais je n'ai trouvé aucun article avec une quantité dans les deux premières colonnes.")
            st.write("Vérifiez que vos noms sont en Colonne A et vos chiffres en Colonne B.")

    except Exception as e:

        st.error(f"Erreur lors de la lecture : {e}")

