sudo docker build -t etl .

sudo docker run --name etl_container --rm --mount type=bind,source=$(pwd)/etl_configs,target=/etl_configs --network=admin_panel_default etl
