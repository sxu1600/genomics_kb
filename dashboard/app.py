from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    node_options = {
        "Disease": ["Statement", "Disease", "Molecular"],
        "Statement": ["Disease", "Drug", "SNV"],
        "Drug": ["Statement"],
        "SNV": ["Statement"],
        "Molecular": ["Disease"]
    }
    property_options = {
        "Disease": ["disease_name", "Neoplastic Status"],
        "Drug": ["drug_name", "drug_status"],
        "SNV": ["gene", "variant"]
    }
    relationship_mapping = {
        ("Disease", "Statement"): "involved",
        ("Statement", "Disease"): "involved",
        ("Disease", "Disease"): "Higher_class",
        ("Disease", "Molecular"): "Molecular_rel",
        ("Molecular", "Disease"): "Molecular_rel",
        ("Statement", "Drug"): "involved",
        ("Statement", "SNV"): "involved",
        ("Drug", "Statement"): "involved",
        ("SNV", "Statement"): "involved",
    }
    relationship_options = {
        "Disease-Statement": ["involved"],
        "Statement-Disease": ["involved"],
        "Disease-Disease": ["Higher_class"],
        "Disease-Molecular": ["Molecular_rel"],
        "Molecular-Disease": ["Molecular_rel"],
        "Statement-Drug": ["involved"],
        "Statement-SNV": ["involved"],
        "Drug-Statement": ["involved"],
        "SNV-Statement": ["involved"],
        # Add other combinations as needed
    }
    
    
    selected_input_node = request.form.get('input_node')
    selected_target_node = request.form.get('target_node')
    selected_relationship = request.form.get('relationship')
    cypher_query = None

    if request.method == 'POST' and selected_input_node and selected_target_node:
        input_node_property = request.form.get('input_node_property')
        input_node_property_value = request.form.get('input_node_property_value')
        target_node_property = request.form.get('target_node_property')
        target_node_property_value = request.form.get('target_node_property_value')

        selected_relationship = relationship_mapping.get(
            (selected_input_node, selected_target_node),
            relationship_mapping.get((selected_target_node, selected_input_node))
        )

        cypher_query = generate_cypher(selected_input_node, input_node_property, input_node_property_value,
                                       selected_target_node, target_node_property, target_node_property_value,
                                       selected_relationship)

    return render_template('index.html', 
                           node_options=node_options, property_options=property_options,
                           relationship_options=relationship_options,
                           selected_input_node=selected_input_node, 
                           selected_target_node=selected_target_node,
                           selected_relationship=selected_relationship,
                           cypher_query=cypher_query)

def generate_cypher(input_node, input_node_property, input_node_property_value, 
                    target_node, target_node_property, target_node_property_value, 
                    relationship):
    """ Generate the Cypher query based on the inputs. """
    query = "MATCH "

    # Aliases for input and target nodes
    input_node_alias = "input" if input_node != target_node else "inputNode"
    target_node_alias = "target" if target_node != input_node else "targetNode"

    # Constructing the MATCH part of the query
    input_node_str = f"({input_node_alias}:{input_node})" if input_node != "NA" else ""
    target_node_str = f"({target_node_alias}:{target_node})" if target_node != "NA" else ""

    # Constructing the relationship part of the query
    if relationship == "involved":
        relationship_str = f"-[:{relationship}]-" if target_node != "NA" else ""
    else:
        relationship_str = f"-[:{relationship}]->" if relationship != "NA" and target_node != "NA" else ""

    # Assembling the query
    query += input_node_str + relationship_str + target_node_str

    # Adding WHERE clause for case-insensitive property value (for both input and target nodes)
    where_clauses = []
    if input_node_property != "NA" and input_node_property_value:
        where_clauses.append(f"{input_node_alias}.{input_node_property} =~'(?i){input_node_property_value}'")
    if target_node_property != "NA" and target_node_property_value:
        where_clauses.append(f"{target_node_alias}.{target_node_property} =~'(?i){target_node_property_value}'")

    if where_clauses:
        query += "\nWHERE " + " AND ".join(where_clauses)

    # RETURN part of the query
    query += "\nRETURN "
    query += target_node_alias if target_node != "NA" else input_node_alias

    return query



if __name__ == '__main__':
    app.run(debug=True)
