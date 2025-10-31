from wmsAdapterV2.utils.utils import exec_query


def save_guide(database: str, delivery_number: str, picking: str, pdf_base64: str):
    try:
        # Guardamos la guia en la base de datos
        sp = """ SET NOCOUNT ON
                EXEC [web].[spi_TDA_EPK_LABELS]
                @codigo_remision = %s
                ,@picking = %s
                ,@pdf = %s
        """

        try:
            exec_query(
                sp,
                (
                    delivery_number,
                    picking,
                    pdf_base64,
                ),
                database=database + "_base",
            )
            return {"message": "Guide saved successfully"}

        except Exception as e:
            print(e)
            raise ValueError({"message": str(e)})

    except Exception as e:
        print(e)
        raise ValueError({"message": str(e)})   