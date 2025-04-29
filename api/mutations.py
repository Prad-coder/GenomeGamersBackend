from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource
from api.jwt_authorize import token_required
from model.mutations import predict_functionality

mutations_api = Blueprint('mutations_api', __name__, url_prefix='/api')
api = Api(mutations_api)

class MutationsAPI:
    class _EditDNA(Resource):
        @token_required()
        def post(self):
            current_user = g.current_user
            body = request.get_json()
            original_strand = body.get('original_strand')
            edits = body.get('edits')

            if not original_strand or not isinstance(edits, list):
                return {'message': 'Invalid input data provided'}, 400

            try:
                strand_list = list(original_strand)
                mutation_records = []
                offset = 0

                for edit in edits:
                    m_type = edit.get('type')
                    pos = edit.get('position')
                    new_base = edit.get('new_base', None)

                    if m_type == "substitution":
                        if new_base not in ['A', 'T', 'C', 'G']:
                            return {'message': 'Invalid base in substitution'}, 400
                        ref_base = strand_list[pos + offset]
                        strand_list[pos + offset] = new_base
                        mutation_type = self.get_mutation_type(ref_base, new_base, m_type)
                        mutation_records.append({
                            'position': pos,
                            'mutation_type': mutation_type,
                            'Reference_Codon': ref_base,
                            'Query_Codon': new_base
                        })

                    elif m_type == "insertion":
                        if new_base not in ['A', 'T', 'C', 'G']:
                            return {'message': 'Invalid base in insertion'}, 400
                        strand_list.insert(pos + offset, new_base)
                        mutation_type = self.get_mutation_type("-", new_base, m_type)
                        mutation_records.append({
                            'position': pos,
                            'mutation_type': mutation_type,
                            'Reference_Codon': "-",
                            'Query_Codon': new_base
                        })
                        offset += 1

                    elif m_type == "deletion":
                        ref_base = strand_list[pos + offset]
                        del strand_list[pos + offset]
                        mutation_type = self.get_mutation_type(ref_base, "-", m_type)
                        mutation_records.append({
                            'position': pos,
                            'mutation_type': mutation_type,
                            'Reference_Codon': ref_base,
                            'Query_Codon': "-"
                        })
                        offset -= 1

                    else:
                        return {'message': 'Invalid mutation type'}, 400

                edited_strand = ''.join(strand_list)

                predictions = []
                for record in mutation_records:
                    input_data = {
                        'Reference_Codon': record['Reference_Codon'],
                        'Query_Codon': record['Query_Codon'],
                        'Mutation_Type': record['mutation_type']
                    }
                    impact = predict_functionality(input_data)
                    predictions.append({
                        'position': record['position'],
                        'mutation_type': record['mutation_type'],
                        'impact': impact
                    })

                return jsonify({
                    'message': 'DNA editing successful',
                    'original_strand': original_strand,
                    'edited_strand': edited_strand,
                    'predictions': predictions
                })

            except Exception as e:
                current_app.logger.error(f"DNA editing error: {str(e)}")
                return {'message': 'DNA editing failed', 'error': str(e)}, 500

        def get_mutation_type(self, reference_base, query_base, edit_type):
            if edit_type == "substitution":
                if reference_base == query_base:
                    return 'Silent Substitution'
                elif query_base in ['TAA', 'TAG', 'TGA']:
                    return 'Nonsense Substitution'
                elif reference_base in ['TAA', 'TAG', 'TGA'] and query_base not in ['TAA', 'TAG', 'TGA']:
                    return 'Read-through Substitution'
                else:
                    return 'Missense Substitution'
            elif edit_type == "insertion":
                return 'In-Frame Insertion'
            elif edit_type == "deletion":
                return 'In-Frame Deletion'
            return 'Missense Substitution'

api.add_resource(MutationsAPI._EditDNA, '/mutations')