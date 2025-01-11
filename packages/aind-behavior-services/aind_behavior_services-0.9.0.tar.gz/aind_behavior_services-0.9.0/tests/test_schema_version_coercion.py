import unittest
from typing import Literal

from pydantic import Field, ValidationError

from aind_behavior_services import AindBehaviorTaskLogicModel
from aind_behavior_services.base import SchemaVersionedModel
from aind_behavior_services.task_logic import TaskParameters

version_pre: str = "0.0.1"
version_post: str = "0.0.2"


class AindBehaviorTaskLogicModelPre(AindBehaviorTaskLogicModel):
    version: Literal[version_pre] = version_pre
    name: str = Field(default="Pre")
    task_parameters: TaskParameters = Field(default=TaskParameters(), validate_default=True)


class AindBehaviorTaskLogicModelPost(AindBehaviorTaskLogicModel):
    version: Literal[version_post] = version_post
    name: str = Field(default="Post")
    task_parameters: TaskParameters = Field(default=TaskParameters(), validate_default=True)


class AindBehaviorTaskLogicModelMajorPost(AindBehaviorTaskLogicModel):
    version: Literal["0.1.0"] = "0.1.0"
    name: str = Field(default="Post")
    task_parameters: TaskParameters = Field(default=TaskParameters(), validate_default=True)


class SchemaVersionedModelPre(SchemaVersionedModel):
    version: Literal[version_post] = version_post
    aind_behavior_services_pkg_version: Literal["0.1.0"] = "0.1.0"


class SchemaVersionedModelPost(SchemaVersionedModel):
    version: Literal[version_post] = version_post
    aind_behavior_services_pkg_version: Literal["0.1.1"] = "0.1.1"


class SchemaVersionedModelMajorPost(SchemaVersionedModel):
    version: Literal[version_post] = version_post
    aind_behavior_services_pkg_version: Literal["1.1.0"] = "1.1.0"


class SchemaVersionCoercionTest(unittest.TestCase):
    def test_version_update_forwards_coercion(self):
        pre_instance = AindBehaviorTaskLogicModelPre()
        post_instance = AindBehaviorTaskLogicModelPost()
        with self.assertLogs(None, level="WARNING") as cm:
            pre_updated = AindBehaviorTaskLogicModelPost.model_validate_json(pre_instance.model_dump_json())
            self.assertIn("Deserialized versioned field 0.0.1, expected 0.0.2. Will attempt to coerce.", cm.output[0])
            self.assertEqual(pre_updated.version, post_instance.version, "Schema version was not coerced correctly.")

    def test_version_update_backwards_coercion(self):
        post_instance = AindBehaviorTaskLogicModelPost()
        major_post_instance = AindBehaviorTaskLogicModelMajorPost()
        with self.assertLogs(None, level="WARNING") as cm:
            self.assertEqual(
                AindBehaviorTaskLogicModelPre.model_validate_json(post_instance.model_dump_json()).version,
                AindBehaviorTaskLogicModelPre().version,
            )
            self.assertIn("Deserialized versioned field 0.0.2, expected 0.0.1. Will attempt to coerce.", cm.output[0])
            with self.assertRaises(ValidationError) as _:
                AindBehaviorTaskLogicModelPre.model_validate_json(major_post_instance.model_dump_json())

    def test_pkg_version_update_forwards_coercion(self):
        pre_instance = SchemaVersionedModelPre()
        post_instance = SchemaVersionedModelPost()
        with self.assertLogs(None, level="WARNING") as cm:
            pre_updated = SchemaVersionedModelPost.model_validate_json(pre_instance.model_dump_json())
            self.assertIn("Deserialized versioned field 0.1.0, expected 0.1.1. Will attempt to coerce.", cm.output[0])
            self.assertEqual(
                pre_updated.aind_behavior_services_pkg_version,
                post_instance.aind_behavior_services_pkg_version,
                "Schema version was not coerced correctly.",
            )

    def test_pkg_version_update_backwards_coercion(self):
        post_instance = SchemaVersionedModelPost()
        major_post_instance = SchemaVersionedModelMajorPost()
        with self.assertLogs(None, level="WARNING") as cm:
            self.assertEqual(
                SchemaVersionedModelPre.model_validate_json(post_instance.model_dump_json()).version,
                SchemaVersionedModelPre().version,
            )
            self.assertIn("Deserialized versioned field 0.1.1, expected 0.1.0. Will attempt to coerce.", cm.output[0])
            with self.assertRaises(ValidationError) as _:
                SchemaVersionedModelPre.model_validate_json(major_post_instance.model_dump_json())


if __name__ == "__main__":
    unittest.main()
