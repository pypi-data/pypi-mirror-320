"""
table.py
-------

This module defines the Table class, which represents a table with
content, read-only indices, and size constraints. It provides methods
and properties to manage a table with content, read-only indices, and
size constraints. It supports operations such as adding, removing, and
retrieving items, as well as setting and getting properties like minimum
and maximum size.

Dependencies:
- copy: Provides deepcopy and copy functions for copying objects.

Functions:
- type_check: Raises a TypeError if the type of the instance is not the 
  type of the desired_type.
- minimum_size_check: Raises a ValueError if the value is less than the
  minimum_size.
- maximum_size_check: Raises a ValueError if the value is greater than
  the maximum_size.
- format_print: Formats and prints the values of an instance based on a
  given format specifier.
- update_arg_dict: A helper function for the Table class magic method
  __call__. Updates the result dictionary with key-value pairs from the
  reference list based on the keys provided in the container tuple. 
  Removes the used key-value pairs from the remaining_args list.
- get_common_checks: Performs common checks on the provided parameters.
- size_error: Raises a KeyError indicating that the size limit has been
  reached.
- type_error: Raises a TypeError with a message indicating the
  unsupported operand types.
- add: Adds the values from another object to the current table.
- sub: Subtracts the values from another object from the current table.
- maximum_iterate: Limits the number of items in an iterable to a 
  specified maximum amount.

Classes:
 - Table: Represents a table with content, read-only indices, and size
   constraints.
"""

from copy import deepcopy, copy

def type_check(instance: any, desired_type: type, property_name: str) -> None:
    """
    Summary
    -------
    Raises a TypeError if the type of the `instance` is not the
    type of the `desired_type`.
    
    Parameters
    ----------
        instance (any): The instance to check.
        desired_type (type): The type that the instance should be.
        property_name (str): The name of the property being checked, 
            used for error messaging.
    
    Raises
    ------
        TypeError: If the type of the instance does not match the 
            desired type.
    """

    instance_type: type = type(instance)
    if instance_type is not desired_type:
        raise TypeError(
            f"{property_name} must be a '{desired_type.__name__}' and not " 
            + f"'{instance_type.__name__}'", instance
        )
    
def minimum_size_check(
        value: int, minimum_size: int, property_name: str) -> None:
    """
    Summary
    -------
    Raises a ValueError if the `value` is less than the 
    `minimum_size`.
    
    Parameters
    ----------
        value (int): The value to check.
        minimum_size (int): The minimum size that the value should be.
        property_name (str): The name of the property being checked, 
            used for error messaging.
    
    Raises
    ------
        ValueError: If the value is less than the minimum size.
    """

    if value < minimum_size:
        raise ValueError(
            f"{property_name}: {value} must be >= {minimum_size}", value
        )
    
def maximum_size_check(
        value: int, maximum_size: int, property_name: str) -> None:
    """
    Summary
    -------
    Raises a ValueError if the `value` is greater than the 
    `maximum_size`.
    
    Parameters
    ----------
        value (int): The value to check.
        maximum_size (int): The maximum size that the value should be.
        property_name (str): The name of the property being checked, 
            used for error messaging.
    
    Raises
    ------
        ValueError: If the value is greater than the maximum size.
    """
    
    if value > maximum_size:
        raise ValueError(
            f"{property_name}: {value} must be <= {maximum_size}", value
        )
    
def format_print(instance: any, format_spec: str) -> str:
    """
    Summary
    -------
    Formats and prints the values of an instance based on a given
    format specifier.
    
    Parameters
    ----------
        instance (any): The instance containing the values to be
            formatted.
        format_spec (str): The format specifier used to filter the
            values.
    
    Returns
    -------
        str: A string representation of the filtered values in the
            instance.
    """

    new_dict = {}
    for value in instance.get_indices(read_only_specifier=format_spec):
        if instance[value] is not None:
            new_dict[value] = instance[value]
    return str(new_dict)

def update_arg_dict(
        container: tuple, reference: list, result: dict,
        remaining_args: list) -> None:
    """
    Summary
    -------
    A helper function for the `Table` class magic method `__call__`.

    Description
    -----------
    Updates the result dictionary with key-value pairs from the
    reference list based on the keys provided in the container
    tuple. Removes the used key-value pairs from the remaining_args
    list.

    Parameters
    ----------
        container (tuple): A tuple containing the keys to be updated
            in the result dictionary.
        reference (list): A list of key-value pairs to be used for
            updating the result dictionary.
        result (dict): The dictionary to be updated with key-value
            pairs from the reference list.
        remaining_args (list): A list of key-value pairs from which
            the used pairs will be removed.
    """

    for arg_name in container:
        for key, value in reference:
            if arg_name == key:
                result[arg_name] = value
                remaining_args.remove((key, value))
                break
    
def get_common_checks(
        maximum_amount: int | None, read_only_specifier: str) -> None:
    """
    Summary
    -------
    Performs common checks on the provided parameters.

    Description
    -----------
    Checks if the maximum_amount is a positive integer and if the
    read_only_specifier is one of the allowed values: "read only",
    "exclude read only", or "all".

    Parameters
    ----------
        maximum_amount (int | None): The maximum number of items to
            retrieve. If not None, it must be a positive integer.
        read_only_specifier (str): Specifies whether to include
            read-only indices. Must be one of "read only", "exclude
            read only", or "all".

    Raises
    ------
        ValueError: If maximum_amount is not a positive integer or if
            read_only_specifier is not one of the allowed values.
    """

    if maximum_amount is not None:
        type_check(
            instance=maximum_amount, desired_type=int,
            property_name="maximum_amount"
        )
        minimum_size_check(
            value=maximum_amount, minimum_size=1,
            property_name="maximum_amount"
        )
    type_check(
        instance=read_only_specifier, desired_type=str,
        property_name="read_only_specifier"
    )
    if not (
        read_only_specifier == "read only"
        or read_only_specifier == "exclude read only"
        or read_only_specifier == "all"
    ):
        raise ValueError(
            "read_only_specifier can only be 'read only', 'all', or "
            + f"'exclude read only' and not '{read_only_specifier}'"
        )
    
def size_error(name: str, value: any) -> None:
    """
    Summary
    -------
    Raises a KeyError indicating that the size limit has been reached.
    
    Parameters
    ----------
        name (str): The name of the size limit, 'minimum' or 'maximum'.
        value (any): The value that cannot be added or removed.
    
    Raises
    ------
        KeyError: If the size limit has been reached.
    """

    action = "remove" if name == "minimum" else "add"
    raise KeyError(
        f"The {name} size has been reached."
        + f" Cannot {action} the value: {value}"
    )

def type_error(action: str, other: any) -> None:
    """
    Summary
    -------
    Raises a TypeError with a message indicating the unsupported
    operand types.
    
    Parameters
    ----------
        action (str): The action being attempted, addition or 
            subtraction.
        other (any): The other operand involved in the operation.
    
    Raises
    ------
        TypeError: Indicates that the operation is not supported
            between a 'Table' and the type of 'other'.
    """

    raise TypeError(
        f"unsupported operand type(s) for {action}: 'Table' and "
        + f"'{type(other).__name__}'"
    )

def add(table: any, other: any) -> any:
    """
    Summary
    -------
    Adds the values from another object to the current `table`.

    Description
    -----------
    If the type of other is the same as table, it iterates over
    the indices and values of other and adds them to table.
    If the types do not match, it raises a TypeError.

    Parameters
    ----------
        table (any): The table to which values will be added.
        other (any): The table from which values will be added.

    Returns
    -------
        any: The updated table with values added from other.

    Raises
    ------
        TypeError: If the type of other is not the same as table.
    """
    if type(other) is type(table):
        for index, value in other:
            table[index] = value
        return table
    type_error(action="+", other=other)

def sub(table: any, other: any) -> any:
    """
    Summary
    -------
    Subtracts the values from another object from the current `table`.

    Description
    -----------
    If the type of other is the same as table, it iterates over
    the indices and values of other and subtracts them from table.
    If the types do not match, it raises a TypeError.

    Parameters
    ----------
        table (any): The table from which values will be subtracted.
        other (any): The table from which values will be subtracted.

    Returns
    -------
        any: The updated table with values subtracted from other.

    Raises
    ------
        TypeError: If the type of other is not the same as table.
    """

    if type(other) is type(table):
        for index, value in other:
            if table[index] is value or table[index] == value:
                table[index] = None
        return table
    type_error(action="-", other=other)

def maximum_iterate(iterable: any, maximum_amount: int | None) -> tuple:
    """
    Summary
    -------
    Limits the number of items in an iterable to a specified maximum 
    amount.

    Description
    -----------
    This function takes an iterable and a maximum amount, and returns a
    tuple containing up to the specified maximum number of items from
    the iterable. If the maximum amount is None, it returns all items
    in the iterable.

    Parameters
    ----------
        iterable (any): The iterable from which items will be taken.
        maximum_amount (int | None): The maximum number of items to 
            include in the returned tuple. If None, all items from the
            iterable are included.

    Returns
    -------
        tuple: A tuple containing up to the specified maximum number of
            items from the iterable.
    """

    if maximum_amount is not None:
        if len(iterable) >= maximum_amount:
            return tuple(list(iterable)[0:maximum_amount])
    return tuple(iterable)

class Table:
    """
    Summary
    -------
    Represents a table with content, read-only indices, and size
    constraints.

    Description
    -----------
    The Table class provides methods and properties to manage a table
    with content, read-only indices, and size constraints. It supports
    operations such as adding, removing, and retrieving items, as well
    as setting and getting properties like minimum and maximum size.

    Properties
    ----------
        minimum_size (int): Gets or sets the minimum size of the Table.
        maximum_size (int | None): Gets or sets the maximum size of the
            Table.
        read_only_indices (set): Gets or sets the read-only indices of
            the Table.
        content (dict): Gets or sets the content of the Table.

    Methods
    -------
        __init__(
            self, content: dict = None, read_only_indices: set = None,
            minimum_size: int = 0,
            maximum_size: int | None = None) -> None:
            Initializes a new instance of the Table class.
        __len__(self) -> int:
            Returns the number of items in the current Table.
        __getitem__(self, index: any) -> any:
            Retrieves the value at the specified index in the current
            Table.
        __setitem__(self, index: any, value: any) -> None:
            Sets the value at the specified index in the current Table.
        __iter__(self) -> iter:
            Returns an iterator for the current Table.
        __contains__(self, value: any) -> bool:
            Checks if a value is contained in the current Table.
        __str__(self) -> str:
            Returns a string representation of the current Table.
        __repr__(self) -> str:
            Returns a detailed string representation of the current
            Table.
        __eq__(self, other: any) -> bool:
            Checks if the current Table is equal to another value.
        __ne__(self, other: any) -> bool:
            Checks if the current Table is not equal to another value.
        __add__(self, other: any) -> any:
            Adds the values from another object to the current Table.
        __iadd__(self, other: any) -> any:
            Adds the values from another object to the current Table
            in place.
        __sub__(self, other: any) -> any:
            Subtracts the values from another object from the current
            Table.
        __isub__(self, other: any) -> any:
            Subtracts the values from another object from the current
            Table in place.
        __deepcopy__(self, memo: dict) -> any:
            Creates a deep copy of the current Table.
        __call__(self, **kwargs) -> tuple:
            Calls the functions stored in the current Table with the
            provided keyword arguments.
        __format__(self, format_spec: str) -> str:
            Formats the Table instance based on the provided format
            specifier.
        __dir__(self) -> list:
            Returns a list of attributes and methods of the current
            Table.
        clone(self) -> any:
            Creates a deep copy of the current Table.
        get_pairs(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
            Retrieves pairs of indices and values from the Table.
        get_indices(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
            Retrieves indices from the Table based on the specified
            maximum amount and read-only specifier.
        get_values(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
            Retrieves values from the Table based on the specified
            maximum amount and read-only specifier.
        find_index(
            self, value: any, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
            Finds indices of the specified value in the Table.
    
    Additional Notes
    ----------------
    Setting an element of a given key in the table to None will remove
    the key-value pair from the table (assuming that removing the
    element will not violate the minimum size rule).
    >>> new_table = Table({0:1, 1:2})
    >>> print(new_table)
    # {0: 1, 1: 2}
    >>> new_table[0] = None
    >>> print(new_table)
    # {1: 2}
    >>> new_table.minimum_size = 1
    >>> new_table[1] = None
    # KeyError: 'The minimum size has been reached. Cannot remove the
    # value: 2'
    """

    @property
    def minimum_size(self) -> int:
        """
        Summary
        -------
        Gets the minimum size of the current `Table`.

        Description
        -----------
        Returns the minimum number of items that the Table must hold.

        Returns
        -------
            int: The minimum size of the Table.
        """

        return self.__minimum_size

    @minimum_size.setter
    def minimum_size(self, value: int) -> None:
        """
        Summary
        -------
        Sets the minimum size for the table.
        
        Description
        -----------
        This method sets the minimum size for the table and performs
        type and value checks to ensure that the provided value is an
        integer and within the valid range.

        Parameters
        ----------
            value (int): The minimum size to be set for the table. Must
                be a non-negative integer and less than or equal to the
                length of the table.
        
        Raises
        ------
            TypeError: If the provided value is not an integer.
            ValueError: If the provided value is less than 0 or greater
                than the length of the table.
        """
        
        type_check(
            instance=value, desired_type=int, 
            property_name="minimum_size"
        )
        minimum_size_check(
            value=value, minimum_size=0,
            property_name="minimum_size"
        )
        maximum_size_check(
            value=value, maximum_size=len(self.__content),
            property_name="minimum_size"
        )
        self.__minimum_size = value

    @property
    def maximum_size(self) -> int | None:
        """
        Summary
        -------
        Gets the maximum size of the current `Table`.

        Description
        -----------
        Returns the maximum number of items that the Table can hold.

        Returns
        -------
            int | None: The maximum size of the Table, or None if there
                is no maximum size.
        """

        return self.__maximum_size

    @maximum_size.setter
    def maximum_size(self, value: int | None) -> None:
        """
        Summary
        -------
        Sets the maximum size for the table.
        
        Description
        -----------
        This method sets the maximum size for the table and performs
        type and value checks to ensure that the provided value is an
        integer and within the valid range.

        Parameters
        ----------
            value (int | None): The maximum size to set. If None, no
                maximum size is enforced.
        
        Raises
        ------
            TypeError: If the value is not an integer.
            ValueError: If the value is less than the current size of
                the table content.
        """

        if value is not None:
            type_check(
                instance=value, desired_type=int, 
                property_name="maximum_size"
            )
            minimum_size_check(
                value=value, 
                minimum_size=len(self.__content),
                property_name="maximum_size"
            )
        self.__maximum_size = value

    @property
    def read_only_indices(self) -> set:
        """
        Summary
        -------
        Returns a set of read-only indices.

        Description
        -----------
        This method provides access to the indices that are marked as
        read-only within the table. These indices cannot be
        modified.
        
        Returns
        -------
            set: A set containing the read-only indices.
        """

        return self.__read_only_indices

    @read_only_indices.setter
    def read_only_indices(self, new_set: set) -> None:
        """
        Summary
        -------
        Sets the read-only indices of the current `Table`.

        Description
        -----------
        Replaces the current read-only indices of the Table with the
        provided set. If the provided value is not a set, it raises a
        TypeError.

        Parameters
        ----------
            value (set): The new read-only indices to set in the Table.

        Raises
        ------
            TypeError: If the provided value is not a set.
        """

        type_check(
            instance=new_set, desired_type=set,
            property_name="read_only_indices"
        )
        self.__read_only_indices = new_set

    @property
    def content(self) -> dict:
        """
        Summary
        -------
        Gets the content of the current `Table`.

        Description
        -----------
        Returns the dictionary containing the content of the Table.

        Returns
        -------
            dict: The content of the Table.
        """

        return self.__content

    @content.setter
    def content(self, new_content: dict) -> None:
        """
        Summary
        -------
        Sets the content of the current `Table`.

        Description
        -----------
        Replaces the current content of the Table with the provided
        dictionary. If the provided value is not a dictionary, it raises
        a TypeError.

        Parameters
        ----------
            value (dict): The new content to set in the Table.

        Raises
        ------
            TypeError: If the provided value is not a dictionary.
        """

        type_check(
            instance=new_content, desired_type=dict, property_name="content"
        )
        self.__content = new_content

    def get_values(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
        """
        Summary
        -------
        Retrieves values from the `Table` based on the specified
        maximum amount and read-only specifier.

        Description
        -----------
        Performs common checks on the provided parameters and retrieves
        values from the Table based on the specified maximum amount and
        read-only specifier.

        Parameters
        ----------
            maximum_amount (int | None, optional): The maximum number of
                values to retrieve. Defaults to None.
            read_only_specifier (str, optional): Specifies whether to
                include read-only values. Defaults to "all".

        Returns
        -------
            tuple: A tuple containing the values from the Table.
        """

        get_common_checks(
            maximum_amount=maximum_amount,
            read_only_specifier=read_only_specifier
        )
        if read_only_specifier == "all":
            return maximum_iterate(
                iterable=self.content.values(), maximum_amount=maximum_amount
            )
        elif read_only_specifier == "read only":
            return_values = []
            for index in self.get_indices(read_only_specifier="read only"):
                return_values.append(self[index])
                if len(return_values) == maximum_amount:
                    break
            return tuple(return_values)
        elif read_only_specifier == 'exclude read only':
            return_values = []
            for index in self.get_indices(
                    read_only_specifier="exclude read only"):
                if (
                    self[index] is not None 
                    and not (index in self.read_only_indices)
                ):
                    return_values.append(self[index])
                    if len(return_values) == maximum_amount:
                        break
            return tuple(return_values)
    
    def get_indices(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
        """
        Summary
        -------
        Retrieves indices from the `Table` based on the specified
        maximum amount and read-only specifier.

        Description
        -----------
        Performs common checks on the provided parameters and retrieves
        indices from the Table based on the specified maximum amount and
        read-only specifier.

        Parameters
        ----------
            maximum_amount (int | None, optional): The maximum number of
                indices to retrieve. Defaults to None.
            read_only_specifier (str, optional): Specifies whether to
                include read-only indices. Defaults to "all".

        Returns
        -------
            tuple: A tuple containing the indices from the Table.
        """

        get_common_checks(
            maximum_amount=maximum_amount,
            read_only_specifier=read_only_specifier
        )
        if read_only_specifier == "all":
            return maximum_iterate(
                iterable=self.content.keys(), maximum_amount=maximum_amount
            )
        elif read_only_specifier == "read only":
            return_values = []
            for index in self.read_only_indices:
                if self[index] is not None:
                    return_values.append(index)
                    if len(return_values) == maximum_amount:
                        break
            return tuple(return_values)
        elif read_only_specifier == 'exclude read only':
            return_values = []
            for index in self.__content.keys():
                if (
                    self[index] is not None 
                    and not (index in self.read_only_indices)
                ):
                    return_values.append(index)
                    if len(return_values) == maximum_amount:
                        break
            return tuple(return_values)

    def find_index(
            self, value: any, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
        """
        Summary
        -------
        Finds indices of the specified value in the `Table`.

        Description
        -----------
        Performs common checks on the provided parameters and retrieves
        indices from the Table based on the specified maximum amount
        and read-only specifier. It then checks if the value at each
        index matches the specified value and returns the matching
        indices.

        Parameters
        ----------
            value (any): The value to find in the Table.
            maximum_amount (int | None, optional): The maximum number of
                indices to retrieve. Defaults to None.
            read_only_specifier (str, optional): Specifies whether to
                include read-only indices. Defaults to "all".

        Returns
        -------
            tuple: A tuple containing the indices where the value is
                found in the Table.
        """

        get_common_checks(
            maximum_amount=maximum_amount,
            read_only_specifier=read_only_specifier
        )
        return_values = []
        for index in self.get_indices(
                maximum_amount=maximum_amount,
                read_only_specifier=read_only_specifier):
            if self[index] == value:
                return_values.append(index)
        return tuple(return_values)

    def clone(self) -> any:
        """
        Summary
        -------
        Creates a deep copy of the current `Table`.

        Description
        -----------
        Uses the deepcopy function to create a deep copy of the current
        Table instance, ensuring that all nested objects are also
        copied.

        Returns
        -------
            any: A deep copy of the current Table.
        """

        return deepcopy(self)

    def get_pairs(
            self, maximum_amount: int | None = None,
            read_only_specifier: str = "all") -> tuple:
        """
        Summary
        -------
        Retrieves pairs of indices and values from the `Table`.

        Description
        -----------
        Performs common checks on the provided parameters and retrieves
        pairs of indices and values from the Table based on the
        specified maximum amount and read-only specifier.

        Parameters
        ----------
            maximum_amount (int | None, optional): The maximum number of
                pairs to retrieve. Defaults to None.
            read_only_specifier (str, optional): Specifies whether to
                include read-only indices. Defaults to "all".

        Returns
        -------
            tuple: A tuple containing pairs of indices and values from
                the Table.
        """

        get_common_checks(
            maximum_amount=maximum_amount,
            read_only_specifier=read_only_specifier
        )
        return_values = []
        for index in self.get_indices(
                maximum_amount=maximum_amount,
                read_only_specifier=read_only_specifier):
            return_values.append((index, self[index]))
        return tuple(return_values)

    def __init__(
            self, content: dict = None, read_only_indices: set = None, 
            minimum_size: int = 0, maximum_size: int | None = None) -> None:
        """
        Summary
        -------
        Initializes a new instance of the `Table` class.

        Description
        -----------
        Sets the initial content, read-only indices, minimum size, and
        maximum size of the Table. If no values are provided, it sets
        default values.

        Parameters
        ----------
            content (dict, optional): The initial content of the Table.
                Defaults to None.
            read_only_indices (set, optional): The indices that are
                read-only. Defaults to None.
            minimum_size (int, optional): The minimum size of the Table.
                Defaults to 0.
            maximum_size (int | None, optional): The maximum size of the
                Table. Defaults to None.
        """

        self.__minimum_size = 0
        self.__maximum_size = None
        self.__content = {}
        self.__read_only_indices = set({})
        if content is not None:
            self.content = content
        if read_only_indices is not None:
            self.read_only_indices = read_only_indices
        if minimum_size != 0:
            self.minimum_size = minimum_size
        if maximum_size is not None:
            self.maximum_size = maximum_size

    def __len__(self) -> int:
        """
        Summary
        -------
        Returns the number of items in the current `Table`.

        Description
        -----------
        Calculates and returns the total number of key-value pairs
        stored in the Table.

        Returns
        -------
            int: The number of items in the Table.
        """

        return len(self.__content)

    def __getitem__(self, index: any) -> any:
        """
        Summary
        -------
        Retrieves the value at the specified index in the current
        `Table`.

        Description
        -----------
        Returns the value associated with the given index in the Table.
        If the index does not exist, it returns None.

        Parameters
        ----------
            index (any): The index of the value to retrieve.

        Returns
        -------
            any: The value at the specified index, or None if the index
                does not exist.
        """

        return self.__content.get(index)
    
    def __setitem__(self, index: any, value: any) -> None:
        """
        Summary
        -------
        Sets the value at the specified index in the current `Table`.

        Description
        -----------
        If the index is in the read-only indices, it raises a KeyError.
        If the current value at the index is not None and the new value
        is None, it checks if the length of the Table is equal to the
        minimum size before removing the item. If the current value is
        None and the new value is not None, it checks if the length of 
        the Table is equal to the maximum size before adding the item.

        Parameters
        ----------
            index (any): The index at which the value will be set.
            value (any): The value to set at the specified index.

        Raises
        ------
            KeyError: If the index is in the read-only indices.
        """

        if index in self.read_only_indices:
            raise KeyError(f"The index is read-only: {index}")
        current_value = self[index]
        if current_value is not None:
            if value is None:
                if len(self) == self.minimum_size:
                    size_error(name="minimum", value=current_value)
                self.__content.pop(index)
            else:
                self.__content[index] = value
        else:
            if value is not None:
                if len(self) == self.maximum_size:
                    size_error(name="maximum", value=value)
                self.__content[index] = value

    def __str__(self) -> str:
        """
        Summary
        -------
        Returns a string representation of the current `Table`.

        Description
        -----------
        Provides a simple string representation of the Table instance,
        showing its content.

        Returns
        -------
            str: A string representation of the Table.
        """

        return str(self.__content)

    def __repr__(self) -> str:
        """
        Summary
        -------
        Returns a string representation of the current `Table`.

        Description
        -----------
        Provides a detailed string representation of the Table
        instance, including its content, read-only indices, minimum
        size, and maximum size.

        Returns
        -------
            str: A string representation of the Table.
        """

        return (
            f"Table(content={self.__content}, "
            + f"read_only_indices={self.__read_only_indices}, "
            + f"minimum_size={self.__minimum_size}, "
            + f"maximum_size={self.__maximum_size})"
        )

    def __iter__(self) -> iter:
        """
        Summary
        -------
        Returns an iterator for the current `Table`.

        Description
        -----------
        Creates an iterator that iterates over the items (key-value
        pairs) in the current Table.

        Returns
        -------
            iter: An iterator over the items in the Table.
        """

        return iter(self.__content.items())

    def __contains__(self, value: any) -> bool:
        """
        Summary
        -------
        Checks if a value is contained in the current `Table`.

        Description
        -----------
        Iterates over the values in the current Table to determine if
        the specified value is present.

        Parameters
        ----------
            value (any): The value to check for in the current Table.

        Returns
        -------
            bool: True if the value is present in the Table, False
                otherwise.
        """

        for other_value in self.__content.values():
            if value == other_value:
                return True
        return False

    def __eq__(self, other: any) -> bool:
        """
        Summary
        -------
        Checks if the current `Table` is equal to another value.

        Description
        -----------
        Compares the current Table with another value to determine if
        they are equal. If the other value is of type Table, it iterates
        over the indices and values of the other Table and compares them
        with the current Table.

        Parameters
        ----------
            other (any): The value to compare with the current Table.

        Returns
        -------
            bool: True if the current Table is equal to the value,
                False otherwise.
        """

        if type(other) == Table:
            if len(other) != len(self):
                return False
            for index, value in other:
                if self[index] != value:
                    return False
            return True
        return False

    def __ne__(self, value) -> bool:
        """
        Summary
        -------
        Checks if the current `Table` is not equal to another value.

        Description
        -----------
        Compares the current Table with another value to determine if
        they are not equal. This is the negation of the equality check.

        Parameters
        ----------
            value (any): The value to compare with the current Table.

        Returns
        -------
            bool: True if the current Table is not equal to the value,
                False otherwise.
        """

        return not self == value

    def __format__(self, format_spec: str) -> str:
        """
        Summary
        -------
        Formats the `Table` instance based on the provided format
        specifier.

        Description
        -----------
        If the format specifier is an empty string, it returns the
        string representation of the Table. If the format specifier
        is "read only" or "exclude read only", it formats the Table
        accordingly. Otherwise, it raises a ValueError.

        Parameters
        ----------
            format_spec (str): The format specifier to format the Table.

        Returns
        -------
            str: The formatted string representation of the Table.

        Raises
        ------
            ValueError: If the format specifier is invalid.
        """
        if format_spec == '':
            return str(self)
        elif format_spec == "read only" or format_spec == "exclude read only":
            return format_print(self, format_spec=format_spec)
        else:
            raise ValueError(
                "format_spec can only be 'read only', 'exclude read only', "
                + f"or '' and not '{format_spec}'"
            )

    def __call__(self, **kwargs) -> tuple:
        """
        Summary
        -------
        Calls the functions stored in the current `Table` with the
        provided keyword arguments.

        Description
        -----------
        Iterates over the functions stored in the current Table,
        prepares the required and optional arguments, and calls each
        function with the appropriate arguments. If a function does not
        accept the required arguments, it is skipped.

        Parameters
        ----------
            **kwargs: The keyword arguments to be passed to the
                functions.

        Returns
        -------
            tuple: A tuple containing the results of the function calls.
        """

        result = []
        for index, function in self:
            if type(function).__name__ == 'function':
                required_arg_count = (
                    function.__code__.co_argcount \
                    - len(function.__defaults__) \
                    if function.__defaults__ \
                    else function.__code__.co_argcount
                )
                accepts_kwargs: int = (
                    1 if function.__code__.co_flags & 0x08 else 0
                )
                accepts_args: int = (
                    1 if function.__code__.co_flags & 0x04 else 0
                )
                optional_args = function.__code__.co_varnames[
                    required_arg_count:len(function.__code__.co_varnames)
                    - accepts_kwargs-accepts_args
                ]
                required_args = function.__code__.co_varnames[
                    :required_arg_count
                ]
                all_arguments = list(kwargs.items())
                remaining_args = all_arguments.copy()
                passing_required_args = dict({})
                passing_optional_args = dict({})
                update_arg_dict(
                    required_args, all_arguments, passing_required_args,
                    remaining_args
                )
                update_arg_dict(
                    optional_args, all_arguments, passing_optional_args,
                    remaining_args
                )
                if len(passing_required_args) == len(required_args):
                    if not accepts_kwargs:
                        result.append((
                            index,
                            function(
                                **passing_required_args, 
                                **passing_optional_args
                            )
                        ))
                    else:
                        result.append((
                            index, 
                            function(
                                **passing_required_args, 
                                **passing_optional_args,
                                **dict(remaining_args)
                            )
                        ))
                else:
                    result.append((index, None))
        return tuple(result)
    
    def __dir__(self) -> list:
        """
        Summary
        -------
        Returns a list of attributes and methods of the current `Table`.

        Description
        -----------
        Iterates over the attributes and methods of the current Table
        instance, formats their names and types, and returns them as a
        sorted list.

        Returns
        -------
            list: A sorted list of attributes and methods with their 
                types.
        """

        result = []
        for name in super().__dir__():
            result.append(
                f"{type(self.__getattribute__(name)).__name__}: '{name}'"
            )
        result.sort()
        return result
    
    def __deepcopy__(self, memo: dict) -> any:
        """
        Summary
        -------
        Creates a deep copy of the current `Table`.

        Description
        -----------
        If the current Table instance is already in the memo dictionary,
        it returns the memoized copy. Otherwise, it creates a new deep 
        copy of the Table and stores it in the memo dictionary.

        Parameters
        ----------
            memo (dict): A dictionary to keep track of already copied 
                objects to avoid infinite recursion.

        Returns
        -------
            any: A deep copy of the current Table.
        """

        if id(self) in memo:
            return memo[id(self)]
        memo[id(self)] = Table(
            deepcopy(self.__content, memo), 
            deepcopy(self.__read_only_indices, memo), 
            copy(self.__minimum_size), copy(self.__maximum_size)
        )
        return memo[id(self)]

    def __add__(self, other: any) -> any:
        """
        Summary
        -------
        Adds the values from another object to the current `Table`.

        Description
        -----------
        If the type of other is the same as Table, it iterates over
        the indices and values of other and adds them to self.
        If the types do not match, it raises a TypeError.

        Parameters
        ----------
            other (any): The table from which values will be added.

        Returns
        -------
            any: A new updated Table with values added from other.

        Raises
        ------
            TypeError: If the type of other is not the same as Table.
        """

        return add(deepcopy(self), other)

    def __iadd__(self, other: any) -> any:
        """
        Summary
        -------
        Adds the values from another object to the current `Table` in
        place.

        Description
        -----------
        If the type of other is the same as Table, it iterates over
        the indices and values of other and adds them to self.
        If the types do not match, it raises a TypeError.

        Parameters
        ----------
            other (any): The table from which values will be added.

        Returns
        -------
            any: The updated Table with values added from other.

        Raises
        ------
            TypeError: If the type of other is not the same as Table.
        """

        return add(self, other)

    def __sub__(self, other: any) -> any:
        """
        Summary
        -------
        Subtracts the values from another object from the current
        `Table`.

        Description
        -----------
        If the type of other is the same as Table, it iterates over
        the indices and values of other and subtracts them from self.
        If the types do not match, it raises a TypeError.

        Parameters
        ----------
            other (any): The table from which values will be subtracted.

        Returns
        -------
            any: A new updated Table with values subtracted from other.

        Raises
        ------
            TypeError: If the type of other is not the same as Table.
        """

        return sub(deepcopy(self), other)

    def __isub__(self, other: any) -> any:
        """
        Summary
        -------
        Subtracts the values from another object from the current 
        `Table` in place.

        Description
        -----------
        If the type of other is the same as Table, it iterates over
        the indices and values of other and subtracts them from self.
        If the types do not match, it raises a TypeError.

        Parameters
        ----------
            other (any): The table from which values will be subtracted.

        Returns
        -------
            any: The updated Table with values subtracted from other.

        Raises
        ------
            TypeError: If the type of other is not the same as Table.
        """

        return sub(self, other)