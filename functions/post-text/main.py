import flask
import requests
import functions_framework
from operator import itemgetter

from google.cloud import storage

BUCKET_NAME = 'trellis-v2-circuity'
CONNECTED_CHARACTERS_OBJECT = 'post-text.json'

# Create Google Cloud Storage client so that I can interact with objects
# stored in Google Cloud Storage buckets.
# Source: https://github.com/googleapis/python-storage/blob/main/samples/snippets/storage_download_into_memory.py
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# I should store characters that are directly connected to this function as a dictionary serialized in a JSON object that is located on Google Cloud Storage. The dictionary key would be the character and the value the corresponding object address or URI. For example: '{"&": "gs://bucket/path/object"}'.
# (January 18, 2025) What I am describing is a JSON object that would store the metadata associated with this function. As such it should follow my standard structure for representing metadata which currently looks like this: '{"direction_nextCharacter_count_probability": "uri"}'.
connected_characters_object = bucket.blob(CONNECTED_CHARACTERS_OBJECT)
connected_characters = connected_characters_object.download_as_bytes().get_json()

def take_step(graph_object):
	"""To take a step, I will first look at the metadata of the current object to see what next steps are listed. From the list of steps, I will randomly pick one. The only factor I will consider when weighting my options will be their power score. I want to pick a powerful one.

	Example object metadata:
		model e: {"nextCharacter_powerValue_absolutePowerValue": "uri"}
	             {"a_0.12_7.34": "gs://path/to/object"}
	The only metadata attached to objects are destinations.

	Args:
		graph_object (google.cloud.storage.blob.Blob): The object with potential destinations in its metadata.
	Returns:
		address (str): Address of the next object I have chosen.
	"""
	metadata = graph_object.metadata

	# possible_destinations[self_link] = powerValue
	possible_destinations = {self_link: path.split('_')[1] for path, self_link in metadata.items()}
	destination = random.choices(
								 population = possible_destinations.keys(),
								 weights = possible_destinations.values()
	)
	return destination

def take_step_recursive(circuit_steps, maximum_circuit_length):
	last_step_object = circuit_steps[-1]
	last_step_metadata = last_step_object.metadata
	possible_destinations = {self_link: path.split('_')[1] for path, self_link in last_step_metadata.items()}
	next_step_address = random.choices(
							   population = possible_destinations.keys(),
							   weights = possible_destinations.values(),
							   k = 1
	)

	if next_step_address == original_object.self_link:
		# Success! I have created a circuit. I will return the most powerful object in this circuit along with the metadata circuit, ordered starting from the most powerful object.
		# most_powerful_object = TODO
		return True, circuit_steps
	elif new_object_address == character_object.self_link:
		# I created a circuit that did not include the original node. I will report my failure.
		logging.debug(f"I failed to create a circuit that included the original node, {original_object.self_link}. I created a circuit of length {len(circuit_steps)} that started and ended at {character_object.self_link}.")
		return False, circuit_steps
	else:
		circuit_steps.append(new_object_address)

	# If I have reached the maximum walk length then I will give up trying to create a circuit.
	if len(circuit_steps) >= maximum_circuit_length:
		logging.debug(f"I failed to create a circuit in {len(circuit_steps)}. I started at {original_object.self_link} and ended at {new_object_address}.")
		return False, circuit_steps
	# Otherwise, I will keep randomly walking.
	else:
		return take_step(circuit_steps, maximum_circuit_length)

def attempt_to_create_circuit_new(original_object, character, bucket, maximum_circuit_length=100):
	"""From the original object, I find a path to an object of the specified character. Then I go forward until I find an object that goes up to a bigger object. From that big object, I go down as far as possible. When it is impossible for me to go down, I go forward until I find either the original object or the character object. If I find the original object first, I win. If I find the character object first, I lose. I have a fixed amount of attempts to try to complete this circuit.

	Args:
		original_object (google.cloud.storage.blob.Blob): The object that I will start from.
		character (str): I will find an object that matches this character.
	Returns:

	"""
	# The initial step in the circuit is the original object
	circuit_steps = [original_object.self_link]

	original_metadata = original_object.metadata
	# I filter out any metadata keys whose first character does not match the character I am looking for.
	matching_character_keys = [key for key in original_metadata.keys() if key[:1] == character]
	# I sort the matching keys in reverse order so that the highest values are at the beginning and then I get the highest value key. I am software that runs on a computer.
	highest_value_character_key = sorted(matching_character_keys, reverse=True)[0]
	highest_value_character_address = original_metadata[highest_value_character_key]

	# Now that I have the highest value character address, I want to get that object
	character_object = bucket.get_blob(highest_value_character_address)
	# Add the character object address to the list of steps in the circuit I am trying to make.
	circuit_steps.append(character_object.self_link)

	return take_step(circuit_steps, maximum_circuit_length)
	"""
	while True:
		# From the character object I am going to randomly walk orthogonally along a series of weighted sets until I find the original object or the character object.
		# I only want to return to the client the object that induces the biggest power differential along the walk; the punchline. I need to track the change in power at every step of my walk.
		new_object_address = take_step(character_object)
		# I only want the original node to be included in the circuit (1) time, so if I walk back to it, I am going to return a result before adding it to the list of steps again.
		# [original, character, object, bigObject, object, original]
		if new_object_address == original_object.self_link:
			# Success! I have created a circuit. I will return the most powerful object in this circuit along with the metadata circuit, ordered starting from the most powerful object.
			most_powerful_object = 


		elif new_object_address == character_object.self_link:
			# I created a circuit that did not include the original node. I will report my failure.
			logging.debug(f"I failed to create a circuit that included the original node, {original_object.self_link}. I created a circuit of length {len(circuit_steps)} that started and ended at {character_object.self_link}.")
			return False
		else:
			circuit_steps.append(new_object_address)

		# If I have reached the maximum walk length then I will give up trying to create a circuit.
		if len(circuit_steps) >= maximum_circuit_length:
			logging.debug(f"I failed to create a circuit in {len(circuit_steps)}. I started at {original_object.self_link} and ended at {new_object_address}.")
			return False
		else:
			return take_step(circuit_steps)
	"""
	
def attempt_to_create_circuit(character_object, origin_object, tries_remaining):
	object_that_goes_up = find_node_that_goes_up(character_object.self_link)
	# Now I have a node that will allow me to go up. I want to go up as high as I can because things that are higher are bigger and bigger is better. Sharing one big idea is more efficient than sharing a bunch of small ideas, but only if the big idea is relevant. In order to predict the relevance of the big idea I am going to try to complete a circuit that goes from the big node to the starting node.
	# Why would the original node ever not be in that circuit?
	big_object = step_up(object_that_goes_up)
	# Once I have a big node, I will keep going down from it until I find a node that does not go down. I will check whether that node is my original node or character node. If it is neither, I will keep stepping from node to node until I find one of them. If I find the original node first, I already know that node connects to the big node via the character node, so I can return `True`. If I find the character node first, then I have completed a circuit without including the original node and my search has failed and I will return `False`. I need to find a circuit that includes the starting node and the character node.
	# How do I keep the origin node and the character node linked to each other?
	path_object = find_node_that_does_not_go_down(big_object)

	result = check_circuit_validity(path_object, origin_object, character_object)
	circuit_validity = result[0]
	step_count = result[1]
	tries_remaining -= 1

	if circuit_validity:
		return True, step_count
	if not circuit_validity and tries_remaining >= 0:
		return attempt_to_create_circuit(character_object, origin_object, tries_remaining)
	else:
		return False, step_count

def check_circuit_validity(path_object, origin_object, character_object, step_count=0, step_limit=32):
	# To avoid creating a process that will create searching forever, I am instituting a firm limit on the amount of steps that may be taken to create a circuit.
	step_count += 1
	if step_count > step_limit:
		raise ValueError(f"You have exceeded the limit of {step_limit} steps in a single circuit.")

	if path_object.self_link == origin_object.self_link:
		return (True, step_count)
	elif path_object.self_link == character_object.self_link:
		return (False, step_count)
	else:
		next_object_in_path = step_forward(path_object)
		return check_circuit_validity(next_object_in_path, origin_object, character_object, step_count)

def find_node_that_goes_up(start_object_uri):
	return NotImplementedError

def find_character_node(original_object, character):
	"""From the original object, I find a path to an object that matches the specified character. How do I do this? The original object has metadata that show the possible paths I can take from this object. Each path has a direction (forward, backwards, up, down). Paths that go up increase the power of my search by a factor of 10 and paths that go down decrease it by a factor of 10. Going forward increases the power of my search by 1 and going backwards decreases the value of my search by 1.

	Directions are represented by values that represent the power change associated with them.
		down:      -10
		backwards: -1
		forwards:   1
		up:         10

	Example object metadata:
		# model d: {"nextCharacter_direction_frequency_count": "uri"}
		#          {"a_1_95_17": "gs://path/to/object"}
	If I add metadata that looks like this to an object, how fast can I retrieve the highest value path?
	"""
	metadata = original_object.metadata

def create_character_object(character):
	character_object = bucket.blob(f"/source_characters/$character")
	character_object.upload_from_string(character)
	# Retrieve the URI for the object
	# Source: https://cloud.google.com/python/docs/reference/storage/latest/google.cloud.storage.blob.Blob#google_cloud_storage_blob_Blob_self_link
	return character_object.self_link

def get_character_object(connected_characters, character):

	character_object_uri = connected_characters.get(character)
	if not character_object_uri:
		character_object_uri = create_character_object(character)
		# Add the new character object to the dictionary of characters
		# connected to this function.
		connected_characters[character] = character_object_uri
	return character_object_uri

@functions_framework.http
def main(request: flask.Request) -> flask.typing.ResponseReturnValue:
	# Receive data from the client. The client sends a character and a set(?) of previous node addresses. Each previous node represents a different dimension. And so, I am starting a search for each node that the client has provided an address for. Previously, I had considered that they would provide a lineage of nodes along a single dimension but what would I do with a lineage? I don't think anything, that's something they can store locally if they want.
	data_from_client = request.get_json()
	# The function takes as input a single character
	character = data_from_client.get(character)
	# The fucntion takes as input a list of node addresses
	origin_addresses = data_from_client.get(path_nodes)

	# Why would I need the URL of this function? I was going to append it to the node_address set. I think that I had some idea of a recursive pattern of calling this function where storing the address would matter. Like, if I stored the entire client request as a URL and then put it into the lineage, but... if I want to get back to the same approximate spot I just provide the same character and address set. That will not guarantee me the same result since the internet is always changing and I use a heuristic search algorithm, but it's as close as you'll get. Otherwise, just store the result on your local machine. Also, I think I envisioned multiple different functions instead of just one. Anyway, I don't think I need this right now.
	#url_of_this_function = 'http://localhost:8080'
	#path_nodes.append(url_of_this_function)

	# I'm going about this all wrong. I want to create the simplest function to create a circuit and then increase the complexity by calling that function from other functions. I should start with the case of a single origin node, character node, and big node. And then create a circuit that connects all (3) of them, in that order.
	origin_object = bucket.blob(node_address)
	result = attempt_to_create_circuit(origin_object, character)

	character_objects = {}
	for origin_address in origin_addresses:
		# Use each provided node as a starting point for the search.
		search_start_object = bucket.blob(node_address) 
		# Maybe I want to modify the `search_start_object` to make it mesh better with the operations I want to do in this function. For instance, I am mostly interested in the metadata attached to the object. I'm going to review the documentation for this and see if there is a more useful and more generic way to represent these nodes.
		# No, actually I am going to design this function to adhere as closely as possible to the native data representations. These are Google Cloud Storage objects. If I want to handle data on other platforms I will write separate functions for those.
		character_object = find_character_node(search_start_object, character)

		# What are the possible values of `character_node`? The `find_character_node` method should always return a node.
		
		# If the address is already registered as a key in the dictionary then increment the value for the item by (1).
		if character_objects.get(character_object.self_link):
			character_objects[character_object.self_link] += 1
		# If the address is not registered in the dictionary, add it and set the initial value to 1 to represent the number of times this node has been encountered.
		else:
			character_objects[character_object.self_link] = 1
	# Now I have a dictionary of unique character nodes and the amount of times I retrieved each one while searching for the specified character from each of the starting nodes. Now that I have all these nodes for the character the client wanted me to search for, I wanted to find the shortest path up and out of here.
	for character_address, observation_count in character_objects.items()
		character_object = bucket.blob(character_address)
		
		result = attempt_to_create_circuit(character_object, origin_object, observation_count)

		object_that_goes_up = find_node_that_goes_up(character_object.self_link)
		# Now I have a node that will allow me to go up. I want to go up as high as I can because things that are higher are bigger and bigger is better. Sharing one big idea is more efficient than sharing a bunch of small ideas, but only if the big idea is relevant. In order to predict the relevance of the big idea I am going to try to complete a circuit that goes from the big node to the starting node.
		# Why would the original node ever not be in that circuit?
		big_object = step_up(object_that_goes_up)
		# Once I have a big node, I will keep going down from it until I find a node that does not go down. I will check whether that node is my original node or character node. If it is neither, I will keep stepping from node to node until I find one of them. If I find the original node first, I already know that node connects to the big node via the character node, so I can return `True`. If I find the character node first, then I have completed a circuit without including the original node and my search has failed and I will return `False`. I need to find a circuit that includes the starting node and the character node.
		# How do I keep the origin node and the character node linked to each other?
		path_object = find_node_that_does_not_go_down(big_object)

		result = check_circuit_validity(path_object, origin_object, character_object)
		circuit_validity = result[0]
		step_count = result[1]

	# Get the metadata of the character
	#character_uri = get_character_object(connected_characters, character)
	#character = bucket.blob(next_character_uri)
	#character_metadata = next_character.metadata
	#path_nodes.append(next_character)

	# What does character metadata look like?
	# model a: {"next_character_z": "count,probability,uri"}
	# model b: {"direction_previousNode_nextCharacter_count_probability": "uri"}
	# model c: {"direction_nextCharacter_count_probability": "uri"}
	ups = []
	for key, value in next_character_metadata.items():
			if key.startswith('up_'):
				value_elements = value.split(',')
				count = value_elements[0]
				probability = value_elements[1]
				up_object_uri = value_elements[2]
				ups.append(tuple(count, probability, up_object_uri))
	if ups:
		up_object = sorted(ups, key=itemgetter[0], reverse=True)
		# Try to complete the cycle by tracing a path from the up_object
		# back to path_nodes[0] using only 'next' relationships
		# If you succeed, store t




	return 

	#return f"Here is your data: {data}."


#import flask
#import functions_framework

#@functions_framework.http
#def hello(request: flask.Request) -> flask.typing.ResponseReturnValue:
#    return "Hello world!"