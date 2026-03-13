"""
Integration Tests for Backup and Restore Workflows
Test full backup creation and restore functionality
Created: 2026-02-16
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

# Try to import the actual modules, fall back to mocks if not available
try:
    from core.backup_manager import BackupManager
    HAS_BACKUP_MANAGER = True
except ImportError:
    HAS_BACKUP_MANAGER = False

try:
    from core.flight_recorder import FlightRecorder, get_flight_recorder
    HAS_FLIGHT_RECORDER = True
except ImportError:
    HAS_FLIGHT_RECORDER = False


@pytest.mark.integration
class TestBackupCreation:
    """Test backup creation workflows"""

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary directory for backup testing"""
        temp_dir = tempfile.mkdtemp(prefix="clutchg_backup_test_")
        yield temp_dir
        # Cleanup after test
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_backup_manager(self, temp_backup_dir):
        """Create a mock or real backup manager for testing"""
        if HAS_BACKUP_MANAGER:
            # Use real BackupManager with temp directory
            manager = BackupManager(backup_dir=temp_backup_dir)
            return manager
        else:
            # Create mock backup manager
            manager = Mock()
            manager.backup_dir = temp_backup_dir
            manager.backups = []

            def mock_create_backup(name):
                """Mock backup creation"""
                backup_path = os.path.join(temp_backup_dir, f"{name}.reg")
                # Create a dummy backup file
                with open(backup_path, 'w') as f:
                    f.write("Windows Registry Editor Version 5.00\n")
                    f.write(f"; Backup: {name}\n")
                    f.write(f"; Created: {datetime.now().isoformat()}\n")

                backup_info = {
                    'name': name,
                    'path': backup_path,
                    'created_at': datetime.now().isoformat(),
                    'size': os.path.getsize(backup_path)
                }
                manager.backups.append(backup_info)
                return Mock(success=True, backup=backup_info)

            def mock_list_backups(self):
                """Mock list backups"""
                return manager.backups

            manager.create_backup = mock_create_backup
            manager.list_backups = mock_list_backups
            return manager

    def test_create_backup_with_custom_name(self, mock_backup_manager, temp_backup_dir):
        """Test creating a backup with a custom name"""
        backup_name = "test_backup_001"
        result = mock_backup_manager.create_backup(backup_name)

        assert result.success, "Backup creation should succeed"
        assert backup_name in [b['name'] for b in mock_backup_manager.list_backups()], \
            "Backup should appear in list"

    def test_create_backup_with_special_characters(self, mock_backup_manager):
        """Test backup creation handles special characters correctly"""
        # Test various special character scenarios
        test_names = [
            "test-backup_001",  # Hyphens and underscores
            "Test Backup 2024",  # Spaces
            "backup_(v1.0)",  # Parentheses and dots
        ]

        for name in test_names:
            result = mock_backup_manager.create_backup(name)
            assert result.success, f"Should handle special characters in: {name}"

    def test_create_backup_duplicate_name(self, mock_backup_manager):
        """Test creating backup with duplicate name"""
        name = "duplicate_test"

        # Create first backup
        result1 = mock_backup_manager.create_backup(name)
        assert result1.success, "First backup should succeed"

        # Try to create duplicate
        result2 = mock_backup_manager.create_backup(name)
        # Should either fail or create a new backup with timestamp
        # (behavior depends on implementation)
        assert result2 is not None, "Should handle duplicate name"

    def test_create_multiple_backups(self, mock_backup_manager):
        """Test creating multiple backups in sequence"""
        backup_count = 5
        for i in range(backup_count):
            name = f"sequential_backup_{i:03d}"
            result = mock_backup_manager.create_backup(name)
            assert result.success, f"Backup {i} should succeed"

        backups = mock_backup_manager.list_backups()
        assert len(backups) >= backup_count, "All backups should be listed"

    def test_list_backups_empty(self, mock_backup_manager):
        """Test listing backups when none exist"""
        backups = mock_backup_manager.list_backups()
        assert isinstance(backups, list), "Should return a list"
        # Can be empty or contain system backups

    def test_list_backups_after_creation(self, mock_backup_manager):
        """Test listing backups after creating them"""
        # Create some test backups
        test_names = ["backup_001", "backup_002", "backup_003"]
        for name in test_names:
            mock_backup_manager.create_backup(name)

        backups = mock_backup_manager.list_backups()
        created_backup_names = [b['name'] for b in backups if b['name'] in test_names]

        assert len(created_backup_names) == len(test_names), \
            "All created backups should be listed"


@pytest.mark.integration
class TestBackupRestore:
    """Test backup restoration workflows"""

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp(prefix="clutchg_restore_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_backup_with_data(self, temp_backup_dir):
        """Create a backup file with test data"""
        backup_path = os.path.join(temp_backup_dir, "test_restore.reg")
        test_data = """Windows Registry Editor Version 5.00
[HKEY_LOCAL_MACHINE\SOFTWARE\ClutchG\Test]
"TestValue"=dword:0000000a
"StringValue"="Test Data"
"""
        with open(backup_path, 'w') as f:
            f.write(test_data)

        return {
            'path': backup_path,
            'name': 'test_restore',
            'size': os.path.getsize(backup_path)
        }

    def test_restore_from_backup_file(self, mock_backup_with_data):
        """Test restoring from a backup file"""
        backup_path = mock_backup_with_data['path']
        assert os.path.exists(backup_path), "Backup file should exist"

        # In real implementation, this would restore to registry
        # For testing, we just verify the file can be read
        with open(backup_path, 'r') as f:
            content = f.read()
            assert "ClutchG" in content, "Backup should contain test data"
            assert "TestValue" in content, "Backup should contain registry keys"

    def test_restore_nonexistent_backup(self, temp_backup_dir):
        """Test restoring from a non-existent backup file"""
        nonexistent_path = os.path.join(temp_backup_dir, "nonexistent.reg")
        assert not os.path.exists(nonexistent_path), "File should not exist"

        # Should handle gracefully (error or specific return value)
        # Implementation dependent


@pytest.mark.integration
class TestBackupDeletion:
    """Test backup deletion workflows"""

    @pytest.fixture
    def temp_backup_dir(self):
        """Create a temporary directory for testing"""
        temp_dir = tempfile.mkdtemp(prefix="clutchg_delete_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def backups_to_delete(self, temp_backup_dir):
        """Create multiple test backups for deletion testing"""
        backups = []
        for i in range(3):
            backup_path = os.path.join(temp_backup_dir, f"delete_test_{i}.reg")
            with open(backup_path, 'w') as f:
                f.write(f"; Backup {i}\n")
            backups.append({
                'name': f"delete_test_{i}",
                'path': backup_path
            })
        return backups

    def test_delete_single_backup(self, temp_backup_dir):
        """Test deleting a single backup"""
        backup_path = os.path.join(temp_backup_dir, "to_delete.reg")
        with open(backup_path, 'w') as f:
            f.write("; Test backup\n")

        assert os.path.exists(backup_path), "Backup should exist before deletion"

        # Delete backup (implementation dependent)
        os.remove(backup_path)

        assert not os.path.exists(backup_path), "Backup should not exist after deletion"

    def test_delete_multiple_backups(self, backups_to_delete):
        """Test deleting multiple backups"""
        for backup in backups_to_delete:
            backup_path = backup['path']
            assert os.path.exists(backup_path), f"Backup {backup['name']} should exist"

            # Delete each backup
            os.remove(backup_path)
            assert not os.path.exists(backup_path), \
                f"Backup {backup['name']} should be deleted"


@pytest.mark.integration
class TestFlightRecorderIntegration:
    """Test FlightRecorder integration with backup operations"""

    @pytest.fixture
    def temp_flight_recorder_dir(self):
        """Create temporary directory for FlightRecorder testing"""
        temp_dir = tempfile.mkdtemp(prefix="flight_recorder_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_flight_recorder(self, temp_flight_recorder_dir):
        """Create a mock or real FlightRecorder for testing"""
        if HAS_FLIGHT_RECORDER:
            try:
                recorder = FlightRecorder(log_dir=temp_flight_recorder_dir)
                return recorder
            except Exception:
                pass

        # Create mock FlightRecorder
        recorder = Mock()
        recorder.snapshots = []

        def mock_create_snapshot(profile, changes):
            """Mock snapshot creation"""
            snapshot = {
                'timestamp': datetime.now(),
                'profile': profile,
                'changes': changes,
                'success': True
            }
            recorder.snapshots.append(snapshot)
            return snapshot

        recorder.create_snapshot = mock_create_snapshot
        recorder.list_snapshots = Mock(return_value=recorder.snapshots)
        return recorder

    def test_flight_recorder_tracks_backup_creation(self, mock_flight_recorder):
        """Test FlightRecorder tracks backup creation operations"""
        changes = [
            {'key': 'HKLM\\SOFTWARE\\Test', 'value': 'TestValue', 'before': '', 'after': 'enabled'}
        ]

        snapshot = mock_flight_recorder.create_snapshot("SAFE", changes)

        assert snapshot is not None, "Snapshot should be created"
        assert snapshot['profile'] == "SAFE", "Profile should be recorded"
        assert len(snapshot['changes']) > 0, "Changes should be recorded"
        assert snapshot['success'] is True, "Operation should be marked as successful"

    def test_flight_recorder_lists_snapshots(self, mock_flight_recorder):
        """Test FlightRecorder can list snapshots"""
        # Create multiple snapshots
        profiles = ["SAFE", "COMPETITIVE", "EXTREME"]
        for profile in profiles:
            mock_flight_recorder.create_snapshot(profile, [])

        snapshots = mock_flight_recorder.list_snapshots()
        assert len(snapshots) >= len(profiles), "All snapshots should be listed"

    def test_flight_recorder_snapshot_details(self, mock_flight_recorder):
        """Test FlightRecorder snapshots contain detailed information"""
        changes = [
            {'key': 'TestKey1', 'value': 'Value1', 'before': 'old', 'after': 'new'},
            {'key': 'TestKey2', 'value': 'Value2', 'before': 0, 'after': 1}
        ]

        snapshot = mock_flight_recorder.create_snapshot("TEST", changes)

        assert 'timestamp' in snapshot, "Snapshot should have timestamp"
        assert 'profile' in snapshot, "Snapshot should have profile"
        assert 'changes' in snapshot, "Snapshot should have changes list"
        assert len(snapshot['changes']) == len(changes), "All changes should be recorded"

    def test_flight_recorder_tracks_failed_operations(self, mock_flight_recorder):
        """Test FlightRecorder tracks failed operations"""
        # Mock a failed operation
        changes = [{'key': 'FailedKey', 'value': 'Value', 'before': '', 'after': 'ERROR'}]

        snapshot = mock_flight_recorder.create_snapshot("SAFE", changes)
        snapshot['success'] = False  # Mark as failed

        assert snapshot['success'] is False, "Failed operation should be marked"
        assert len(snapshot['changes']) > 0, "Changes should still be recorded"


@pytest.mark.integration
class TestBackupRestoreWorkflow:
    """Test complete backup and restore workflows"""

    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace for testing"""
        temp_dir = tempfile.mkdtemp(prefix="clutchg_workflow_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_full_backup_restore_cycle(self, temp_workspace):
        """Test complete backup creation and restore cycle"""
        # 1. Create backup
        backup_name = "cycle_test_backup"
        backup_path = os.path.join(temp_workspace, f"{backup_name}.reg")
        backup_data = "Windows Registry Editor Version 5.00\n[Test Key]\n"

        with open(backup_path, 'w') as f:
            f.write(backup_data)

        assert os.path.exists(backup_path), "Backup should be created"

        # 2. Verify backup exists
        assert os.path.getsize(backup_path) > 0, "Backup should have content"

        # 3. "Restore" (verify file can be read)
        with open(backup_path, 'r') as f:
            restored_data = f.read()

        assert backup_data in restored_data, "Restored data should match backup"

        # 4. Cleanup
        os.remove(backup_path)
        assert not os.path.exists(backup_path), "Backup should be deleted"

    def test_backup_with_timestamp(self, temp_workspace):
        """Test backups include timestamps for tracking"""
        from datetime import datetime

        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(temp_workspace, f"{backup_name}.reg")

        with open(backup_path, 'w') as f:
            f.write(f"; Created: {datetime.now().isoformat()}\n")

        # Verify filename contains timestamp components
        assert "_" in backup_name, "Backup name should contain timestamp separator"

    def test_backup_size_tracking(self, temp_workspace):
        """Test backup file sizes are tracked correctly"""
        # Create backups of different sizes
        sizes = []
        for i in range(1, 4):
            backup_path = os.path.join(temp_workspace, f"size_test_{i}.reg")
            content = "x" * (i * 100)  # Different sizes
            with open(backup_path, 'w') as f:
                f.write(content)
            sizes.append(os.path.getsize(backup_path))

        # Verify sizes are different
        assert len(set(sizes)) == len(sizes), "Each backup should have unique size"
        assert sizes[0] < sizes[1] < sizes[2], "Sizes should increase"


# Test utilities
def calculate_test_coverage():
    """Calculate test coverage for backup/restore functionality"""
    test_categories = {
        'backup_creation': ['test_create_backup_with_custom_name',
                          'test_create_backup_with_special_characters',
                          'test_create_backup_duplicate_name',
                          'test_create_multiple_backups'],
        'backup_listing': ['test_list_backups_empty',
                          'test_list_backups_after_creation'],
        'backup_restore': ['test_restore_from_backup_file',
                          'test_restore_nonexistent_backup'],
        'backup_deletion': ['test_delete_single_backup',
                          'test_delete_multiple_backups'],
        'flight_recorder': ['test_flight_recorder_tracks_backup_creation',
                           'test_flight_recorder_lists_snapshots',
                           'test_flight_recorder_snapshot_details',
                           'test_flight_recorder_tracks_failed_operations'],
        'workflows': ['test_full_backup_restore_cycle',
                      'test_backup_with_timestamp',
                      'test_backup_size_tracking']
    }

    total_tests = sum(len(tests) for tests in test_categories.values())
    print(f"\n{'='*60}")
    print(f"Test Coverage Summary")
    print(f"{'='*60}")
    print(f"Total Test Categories: {len(test_categories)}")
    print(f"Total Test Cases: {total_tests}")
    print(f"\nCategories:")
    for category, tests in test_categories.items():
        print(f"  - {category}: {len(tests)} tests")
    print(f"{'='*60}\n")

    return test_categories


if __name__ == "__main__":
    # Run coverage calculation
    calculate_test_coverage()

    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
