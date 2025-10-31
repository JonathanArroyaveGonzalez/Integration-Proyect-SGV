from wmsAdapterV2.utils.utils import exec_query


def cancel_guide(database: str, delivery_number: str, picking: str):
    try:
        sp = """ SET NOCOUNT ON
                EXEC [web].[Agw_typeAnularGuiaIn] %s, %s"""

        try:
            guia_anulada = exec_query(
                sp,
                (
                    delivery_number,
                    picking,
                ),
                database=database + "_base",
            )
            print(guia_anulada)
            return {"message": "Guide deleted successfully"}

        except Exception as e:
            print(e)
            raise ValueError({"message": str(e)})

    except Exception as e:
        print(e)
        raise ValueError({"message": str(e)})