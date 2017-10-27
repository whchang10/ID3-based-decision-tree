import copy
import attributes


def entropy_by_attribute(dataset, attribute, classifier):
  total_size = len(dataset)
  subsets_collection = dataset.subset(attribute)

  entropy = 0
  for subset in subsets_collection:
    entropy += len(subset) / float(total_size) * subset.entropy(classifier)

  return entropy


def find_split_attribute(dataset, attribute_set, classifier):
  split_attribute = attribute_set[0]
  min_entropy = -1
  for attribute in attribute_set:
    entropy = entropy_by_attribute(dataset, attribute, classifier)
    if min_entropy == -1 or entropy < min_entropy:
      min_entropy = entropy
      split_attribute = attribute

  return split_attribute

class DNode:
  def __init__(self, classifier, training_data, attribute_set, branch_name=False, branch_attribute=False, parent=False, indent=""):
    self.classifier = classifier
    self.training_data = training_data
    self.attribute_set = attribute_set
    self.branch_name = branch_name
    self.branch_attribute = branch_attribute
    self.parent = parent
    self.indent = indent

    self.classification = False
    self.children = []
    return

  def is_leaf_node(self):
    if len(self.children) == 0:
      return True
    return False


  def dump(self):
    if self.parent:
      print self.indent + self.branch_name + ':' + self.branch_attribute
      if self.is_leaf_node():
        assert self.classification
        print self.indent + ' ' + '<' + self.classification + '>'
    elif self.is_leaf_node():
      print '<' + self.classification + '>'

    for child in self.children:
      child.dump()


  def get_classification(self):
    if self.classification == False:
      self.classification = self.training_data.majority(self.classifier)
      if self.classification is None:
        if self.parent:
          self.classification = self.parent.get_classification()
        else:
          self.classification = self.training_data.majority(self.classifier, True)
    return self.classification


  def create_leaf_nodes(self, split_attribute):
      childern_datasets = self.training_data.subset(split_attribute)
      childern_attribute = copy.deepcopy(self.attribute_set)
      childern_attribute.remove(split_attribute.name)

      indent = ''
      if self.parent:
        indent = self.indent + ' '

      for index, child_dataset in enumerate(childern_datasets):
        self.children.append(DNode(self.classifier, child_dataset, childern_attribute,\
                                   split_attribute.name, split_attribute.values[index], self, indent))


  def build_sub_tree(self):
    if len(self.training_data) == 0:
      self.classification = self.parent.get_classification()
    elif self.training_data.is_well_classified(self.classifier):
      self.classification = self.training_data.majority(self.classifier)
    elif len(self.attribute_set) == 0:
      self.classification = self.training_data.majority(self.classifier)
      if self.classification is None:
        self.classification = self.parent.get_classification()
    else:
      split_attribute = find_split_attribute(self.training_data, self.attribute_set, self.classifier)
      split_attribute.values = sorted(split_attribute.values)
      self.create_leaf_nodes(split_attribute)
      for child in self.children:
        child.build_sub_tree()


class DTree:
  'Represents a decision tree created with the ID3 algorithm'

  def __init__(self, classifier, training_data, attribute_set):
    self.classifier = classifier
    self.training_data = training_data
    self.attribute_set = attributes.Attributes(False, sorted(attribute_set, key = lambda attribute: attribute.name))
    self.root = None

    self.build_decision_tree()
    return


  def evaluate(self, classifier, test_example, node):
    if node.is_leaf_node():
      if test_example.get_value(classifier) == node.get_classification():
        return 1
      else:
        return 0
    else:
      for child in node.children:
          if test_example.get_value(child.branch_name) == child.branch_attribute:
            return self.evaluate(classifier, test_example, child)

  def test(self, classifier, testing_data):
    if self.root is None:
      return 0

    count = 0
    for test_example in testing_data:
      count += self.evaluate(classifier, test_example, self.root)
    return count

  def dump(self):
    self.root.dump()
    return ""

  @staticmethod
  def information_gain(entropy, splited_entropy):
    return entropy - splited_entropy

  def build_decision_tree(self):
    self.root = DNode(self.classifier, self.training_data, self.attribute_set)
    self.root.build_sub_tree()
    return


