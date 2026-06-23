import streamlit as st
import pandas as pd


def render_admin(sql_conn, clear_cache_func):
    st.title("DATABASE ADMINISTRATION")
    st.text("Secure CRUD Management Console")
    st.divider()

    if sql_conn:
        try:
            st.subheader("Hardware and Games Explorer")
            explore_tab1, explore_tab2, explore_tab3 = st.tabs(
                ["Registered Games", "Registered CPUs", "Registered GPUs"])

            with explore_tab1:
                query_games_exp = """
                    SELECT g.Game_ID, g.Title, c.Category_Name, g.Developer, g.Release_Year, g.Storage_Required_GB 
                    FROM GAMES g LEFT JOIN GAME_CATEGORIES c ON g.Category_ID = c.Category_ID 
                    ORDER BY g.GAME_ID
                """
                df_all_games = pd.read_sql(query_games_exp, con=sql_conn)
                st.dataframe(df_all_games, width="stretch", hide_index=True)

            with explore_tab2:
                df_all_cpus = pd.read_sql("SELECT * FROM CPUS ORDER BY CPU_ID", con=sql_conn)
                st.dataframe(df_all_cpus, width="stretch", hide_index=True)

            with explore_tab3:
                df_all_gpus = pd.read_sql("SELECT * FROM GPUS ORDER BY GPU_ID", con=sql_conn)
                st.dataframe(df_all_gpus, width="stretch", hide_index=True)

            st.divider()

            st.subheader("Database Record Management")

            df_categories = pd.read_sql("SELECT Category_ID, Category_Name FROM GAME_CATEGORIES", con=sql_conn)
            category_map = {}
            if not df_categories.empty:
                category_map = dict(zip(df_categories['CATEGORY_NAME'], df_categories['CATEGORY_ID']))

            add_tab, up_tab, del_tab1, del_tab2, del_tab3 = st.tabs(
                ["Add Game", "Update Game", "Delete Game", "Delete CPU", "Delete GPU"])

            with add_tab:
                if not df_categories.empty:
                    with st.form("add_game_form"):
                        new_title = st.text_input("Game Title")
                        new_dev = st.text_input("Developer Studio")

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            new_year = st.number_input("Release Year", min_value=1990, max_value=2030, step=1,
                                                       value=2024)
                        with col2:
                            new_storage = st.number_input("Storage Required (GB)", min_value=1.0, step=1.0, value=50.0)
                        with col3:
                            new_cat_name = st.selectbox("Game Category", list(category_map.keys()))

                        if st.form_submit_button("Insert Game Record", type="primary"):
                            if new_title.strip() == "":
                                st.error("Game Title cannot be empty.")
                            else:
                                cursor = sql_conn.cursor()
                                cursor.execute("SELECT COALESCE(MAX(Game_ID), 0) + 1 FROM GAMES")
                                next_id = cursor.fetchone()[0]

                                target_cat_id = category_map[new_cat_name]

                                insert_query = """
                                    INSERT INTO GAMES (Game_ID, Title, Developer, Release_Year, Category_ID, Storage_Required_GB) 
                                    VALUES (:1, :2, :3, :4, :5, :6)
                                """
                                cursor.execute(insert_query,
                                               [next_id, new_title, new_dev, new_year, target_cat_id, new_storage])
                                sql_conn.commit()
                                clear_cache_func()
                                st.success(
                                    f"Success! {new_title} has been added to the registry. Refresh the page to view.")
                else:
                    st.error("GAME_CATEGORIES table is missing or empty. Cannot process games without categories.")

            with up_tab:
                if not df_all_games.empty and category_map:
                    target_update_game = st.selectbox("Select Game to Update:", df_all_games['TITLE'].tolist(),
                                                      key="update_game_select")

                    curr_data = df_all_games[df_all_games['TITLE'] == target_update_game].iloc[0]
                    curr_cat_name = curr_data['CATEGORY_NAME'] if pd.notna(curr_data['CATEGORY_NAME']) else \
                    list(category_map.keys())[0]
                    curr_cat_index = list(category_map.keys()).index(
                        curr_cat_name) if curr_cat_name in category_map else 0

                    with st.form("update_game_form"):
                        up_title = st.text_input("Update Game Title", value=curr_data['TITLE'])
                        up_dev = st.text_input("Update Developer Studio",
                                               value=curr_data['DEVELOPER'] if pd.notna(curr_data['DEVELOPER']) else "")

                        ucol1, ucol2, ucol3 = st.columns(3)
                        with ucol1:
                            up_year = st.number_input("Update Release Year", min_value=1990, max_value=2030, step=1,
                                                      value=int(curr_data['RELEASE_YEAR']) if pd.notna(
                                                          curr_data['RELEASE_YEAR']) else 2024)
                        with ucol2:
                            up_storage = st.number_input("Update Storage Required (GB)", min_value=1.0, step=1.0,
                                                         value=float(curr_data['STORAGE_REQUIRED_GB']) if pd.notna(
                                                             curr_data['STORAGE_REQUIRED_GB']) else 50.0)
                        with ucol3:
                            up_cat_name = st.selectbox("Update Game Category", list(category_map.keys()),
                                                       index=curr_cat_index)

                        if st.form_submit_button("Commit Updates to Database", type="primary"):
                            if up_title.strip() == "":
                                st.error("Game Title cannot be empty.")
                            else:
                                cursor = sql_conn.cursor()
                                target_up_cat_id = category_map[up_cat_name]

                                update_query = """
                                    UPDATE GAMES 
                                    SET Title = :1, Developer = :2, Release_Year = :3, Category_ID = :4, Storage_Required_GB = :5
                                    WHERE Title = :6
                                """
                                cursor.execute(update_query, [up_title, up_dev, up_year, target_up_cat_id, up_storage,
                                                              target_update_game])
                                sql_conn.commit()
                                clear_cache_func()
                                st.success(f"Success! {target_update_game} has been updated. Refresh the page to view.")
                else:
                    st.info("No games available to update.")

            with del_tab1:
                st.warning("Warning: Deleting records will permanently remove them from the Oracle database.")
                df_games_list = pd.read_sql("SELECT Title FROM GAMES ORDER BY Title", con=sql_conn)
                if not df_games_list.empty:
                    target_game = st.selectbox("Select Game to Delete:", df_games_list['TITLE'].tolist())
                    if st.button("Delete Selected Game", type="primary"):
                        cursor = sql_conn.cursor()
                        cursor.execute("DELETE FROM GAMES WHERE Title = :1", [target_game])
                        sql_conn.commit()
                        clear_cache_func()
                        st.success("Record deleted successfully. Please refresh the page.")
                else:
                    st.info("No games available to delete.")

            with del_tab2:
                st.warning("Warning: Deleting records will permanently remove them from the Oracle database.")
                df_cpus_list = pd.read_sql("SELECT Model FROM CPUS ORDER BY Model", con=sql_conn)
                if not df_cpus_list.empty:
                    target_cpu = st.selectbox("Select CPU to Delete:", df_cpus_list['MODEL'].tolist())
                    if st.button("Delete Selected CPU", type="primary"):
                        cursor = sql_conn.cursor()
                        cursor.execute("DELETE FROM CPUS WHERE Model = :1", [target_cpu])
                        sql_conn.commit()
                        clear_cache_func()
                        st.success("Record deleted successfully. Please refresh the page.")
                else:
                    st.info("No CPUs available to delete.")

            with del_tab3:
                st.warning("Warning: Deleting records will permanently remove them from the Oracle database.")
                df_gpus_list = pd.read_sql("SELECT Model FROM GPUS ORDER BY Model", con=sql_conn)
                if not df_gpus_list.empty:
                    target_gpu = st.selectbox("Select GPU to Delete:", df_gpus_list['MODEL'].tolist())
                    if st.button("Delete Selected GPU", type="primary"):
                        cursor = sql_conn.cursor()
                        cursor.execute("DELETE FROM GPUS WHERE Model = :1", [target_gpu])
                        sql_conn.commit()
                        clear_cache_func()
                        st.success("Record deleted successfully. Please refresh the page.")
                else:
                    st.info("No GPUs available to delete.")

        except Exception as ex:
            st.error(f"Failed to execute administrative transaction: {str(ex)}")
    else:
        st.error("Oracle database controller offline.")