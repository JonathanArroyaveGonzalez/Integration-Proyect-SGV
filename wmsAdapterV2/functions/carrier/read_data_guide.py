from wmsAdapterV2.utils.utils import exec_query


def read_data_guide(database: str, picking: str, bigpedido: str, is_detail: int):
    try:
        sp = """ SET NOCOUNT ON
        EXEC [web].[Agw_typeGenerarGuiaIn] %s , %s, %s """
        try:
            if is_detail:
                data_type = 1
            else:
                data_type = 0

            # traemos la informacion de tte
            tte = exec_query(
                sp,
                (
                    picking,
                    bigpedido,
                    data_type,
                ),
                database=database + "_base",
            )
            return tte

        except Exception as e:
            print(e)
            raise ValueError(str(e))

    except Exception as e:
        print(e)
        raise ValueError(str(e))