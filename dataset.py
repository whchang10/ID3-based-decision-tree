import math
import re
import sys

class Example:
  'An individual example with values for each attribute'

  def __init__(self, values, attributes, filename, line_num):
    if len(values) != len(attributes):
      sys.stderr.write(
        "%s: %d: Incorrect number of attributes (saw %d, expected %d)\n" %
        (filename, line_num, len(values), len(attributes)))
      sys.exit(1)
    # Add values, Verifying that they are in the known domains for each
    # attribute
    self.values = {}
    for ndx in range(len(attributes)):
      value = values[ndx]
      attr = attributes.attributes[ndx]
      if attr.values[0] != "continuous":
        if value not in attr.values:
          sys.stderr.write(
            "%s: %d: Value %s not in known values %s for attribute %s\n" %
            (filename, line_num, value, attr.values, attr.name))
          sys.exit(1)
      else:
        value = float(value)
      self.values[attr.name] = value


  # Find a value for the specified attribute, which may be specified as
  # an Attribute instance, or an attribute name.
  def get_value(self, attr):
    if isinstance(attr, str):
      return self.values[attr]
    else:
      return self.values[attr.name]
    

class DataSet:
  'A collection of instances, each representing data and values'

  def __init__(self, data_file=False, attributes=False, all_examples=False):
    self.all_examples = []
    if data_file:
      line_num = 1
      num_attrs = len(attributes)
      for next_line in data_file:
        next_line = next_line.rstrip()
        next_line = re.sub(".*:(.*)$", "\\1", next_line)
        attr_values = next_line.split(',')
        new_example = Example(attr_values, attributes, data_file.name, line_num)
        self.all_examples.append(new_example)
        line_num += 1

    if all_examples:
      self.all_examples = all_examples

  def __len__(self):
    return len(self.all_examples)

  def __getitem__(self, key):
    return self.all_examples[key]

  def append(self, example):
    self.all_examples.append(example)

  # Determine the entropy of a collection with respect to a classifier.
  # An entropy of zero indicates the collection is completely sorted.
  # An entropy of one indicates the collection is evenly distributed with
  # respect to the classifier.
  def entropy(self, classifier):
    dataset_size = len(self.all_examples)
    classifier_name = classifier.name
    classifier_value_set = classifier.values

    if dataset_size == 0:
      return 0

    subset_sizes = []
    for value in classifier_value_set:
      subset_sizes.append(len([example for example in self.all_examples if example.get_value(classifier_name) == value]))

    subset_portions = [subset_size / (float)(dataset_size) for subset_size in subset_sizes]

    dataset_entropy = 0
    for subset_portion in subset_portions:
      if subset_portion != 0:
        dataset_entropy += -1 * subset_portion * math.log(subset_portion, 2)

    return dataset_entropy


  def subset(self, attribute, index=-1):
    attribute_name = attribute.name
    attribute_value_set = attribute.values

    subsets_collection = []
    if attribute_value_set[0] != "continuous":
      for value in attribute_value_set:
        subset = [example for example in self.all_examples if example.get_value(attribute_name) == value]
        subsets_collection.append(DataSet(False, False,subset))
    else:
      self.all_examples.sort(key=lambda example: example.values[attribute_name])
      subset_left = self.all_examples[0:index + 1]
      subsets_collection.append(DataSet(False, False, subset_left))
      assert index + 1 < len(self.all_examples)
      if index + 1 < len(self.all_examples):
        subset_right = self.all_examples[index + 1:]
        subsets_collection.append(DataSet(False, False, subset_right))

    return subsets_collection


  def majority(self, classifier, is_root=False):
    classifier_name = classifier.name
    classifier_value_set = sorted(classifier.values)

    if len(self.all_examples) == 0:
      return None

    subset_sizes = []
    for value in classifier_value_set:
      subset_sizes.append(len([example for example in self.all_examples if example.get_value(classifier_name) == value]))

    max_subset_size = max(subset_sizes)
    if is_root == False and len([subset_size for subset_size in subset_sizes if subset_size == max_subset_size]) > 1:
        return None

    majority_index = subset_sizes.index(max_subset_size)
    value = classifier_value_set[majority_index]

    return value

  def is_well_classified(self, classifier):
    classifier_name = classifier.name
    classifier_value_set = sorted(classifier.values)

    assert len(self.all_examples) > 0

    subset_sizes = []
    for value in classifier_value_set:
      size = len([example for example in self.all_examples if example.get_value(classifier_name) == value])
      if size != 0:
        subset_sizes.append(size)

    if len(subset_sizes) == 1:
      return True

    return False