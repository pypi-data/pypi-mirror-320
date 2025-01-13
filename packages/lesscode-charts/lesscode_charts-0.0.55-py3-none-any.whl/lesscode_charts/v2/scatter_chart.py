"""
散点图
"""


class ScatterChart:

    @staticmethod
    def scatter(data: list, title=""):
        """
            {
                series: [
                    {
                        data: [
                            { name: '点的名称，可不提供',
                              lon :'',
                              lat: '',
                              value: 100
                            }
                        ]
                    }
                ],
            }
        :return:
        """
        for d in data:
            if not d.get("value"):
                d["value"] = 100
        result = {
            "chart_type": "scatter",
            "series": [{
                "data": data
            }],
            "title": title,
        }
        return result
