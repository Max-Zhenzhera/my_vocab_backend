#!/bin/bash

migrations_dir="app/db/migrations/versions"
for migration_file in ${migrations_dir}/*.py; do
    echo >> "$migration_file"
    header="Enums drop"
    echo "    # ### $header" >> "$migration_file"

    enum_db_names=$(rg "postgresql\.ENUM\(.*, name='(.*)'\)" "$migration_file" -o -r '$1')
    for enum_db_name in $enum_db_names; do
        drop_command="sa.Enum(name='$enum_db_name').drop(op.get_bind())"
        echo "    $drop_command" >> "$migration_file"
    done

    footer="end $header"
    echo "    # ### $footer" >> "$migration_file"
done
