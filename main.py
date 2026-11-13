    if st.button(t["btn_analyser"]):
      if not description_reve.strip():
        st.warning("Veuillez raconter votre rêve avant de lancer l'analyse.")
      else:
        with st.spinner("Analyse approfondie du subconscient en cours..."):
          st.success("Analyse détaillée terminée !")

          # Analyse détaillée structurée
          st.markdown("### 🔮 Analyse et Interprétation Profonde")

          st.markdown("#### 1. 🌊 Symbolique principale")
          st.write(
              f"Votre rêve met en scène l'émotion de **{emotion}** avec un"
              f" niveau de lucidité de **{lucidite}/5**. Votre récit met en"
              " lumière le flux de vos émotions et de votre inconscient en"
              " mouvement face à une situation actuelle."
          )

          st.markdown("#### 2. 🧠 Clé psychologique")
          st.write(
              "Ce scénario onirique traduit une phase de transition ou un"
              " besoin de lâcher-prise. Votre esprit cherche à réorganiser"
              " des informations pour retrouver un équilibre intérieur."
          )

          st.markdown("#### 3. 🌱 Conseil de votre subconscient")
          st.write(
              "Accordez-vous un moment de calme pour identifier ce qui pèse"
              " sur votre charge mentale et accepter de ne pas tout contrôler."
          )

          user.dreams_count += 1
          db.commit()
